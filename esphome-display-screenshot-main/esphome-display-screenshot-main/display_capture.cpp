// display_capture -- implementation file.
//
// IMPORTANT: The #define protected public hack MUST be the very first thing
// in this file, before any #include. It makes DisplayBuffer::buffer_ accessible
// in this translation unit only. The .h file uses forward declarations so it
// compiles cleanly without this hack.
//
// This works because each .cpp is a separate translation unit with its own
// #pragma once state. The macro only affects headers included in THIS file.

// --- Step 1: Expose protected members for buffer access ---
#define protected public
#include "esphome/components/display/display_buffer.h"
#include "esphome/components/display/display.h"
#undef protected

#ifdef USE_RPI_DPI_RGB
#include "esphome/components/rpi_dpi_rgb/rpi_dpi_rgb.h"
#endif

// --- Step 2: Our own header (uses only forward declarations, no buffer access) ---
#include "display_capture.h"

// --- Step 3: Globals support (conditionally compiled) ---
// DISPLAY_CAPTURE_USE_GLOBALS is defined by __init__.py when page_global or
// sleep_global are configured. Without this guard, the build fails when globals
// aren't used because ESPHome doesn't copy globals headers to the build directory.
#ifdef DISPLAY_CAPTURE_USE_GLOBALS
#include "esphome/components/globals/globals_component.h"
#endif

#include <esp_heap_caps.h>
#include <cstring>

namespace esphome {
namespace display_capture {

// ============================================================================
// Component lifecycle
// ============================================================================

void DisplayCaptureHandler::setup() {
  // Binary semaphore for HTTP task <-> main loop synchronization.
  // The HTTP handler takes it (blocks), the main loop gives it (unblocks).
  this->semaphore_ = xSemaphoreCreateBinary();
  this->base_->init();
  this->base_->add_handler(this);

  const char *mode_str = "single";
  if (this->page_mode_ == NATIVE_PAGES)
    mode_str = "native_pages";
  else if (this->page_mode_ == GLOBAL_PAGES)
    mode_str = "global_pages";

  const char *backend_str = "display_buffer";
  if (this->backend_ == BACKEND_RPI_DPI_RGB)
    backend_str = "rpi_dpi_rgb";

  int pages = this->get_page_count();
  if (pages >= 0) {
    ESP_LOGI(TAG, "Display capture registered at /screenshot (mode: %s, backend: %s, pages: %d)", mode_str, backend_str, pages);
  } else {
    ESP_LOGI(TAG, "Display capture registered at /screenshot (mode: %s, backend: %s, pages: unknown)", mode_str, backend_str);
  }
}

int DisplayCaptureHandler::get_page_count() const {
  switch (this->page_mode_) {
    case NATIVE_PAGES:
      return this->pages_.size();
    case GLOBAL_PAGES:
      // Global mode doesn't inherently know the page count -- use page_names
      // as the source of truth if provided, otherwise return -1 (unknown).
      // The /info endpoint omits the "pages" field when the count is unknown,
      // so clients can distinguish "unknown" from "zero pages".
      return this->page_names_.empty() ? -1 : this->page_names_.size();
    default:
      return 1;
  }
}

// ============================================================================
// Main loop -- runs on the ESPHome main task
// ============================================================================
//
// This is where all display buffer access happens. The HTTP task sets
// request_pending_ and blocks on the semaphore. We do the work here
// (where it's safe to touch display state) and signal when done.
//
// Sequence:
//   1. Wake display if sleeping (global pages mode)
//   2. Switch to requested page (if ?page=N was specified)
//   3. Render: display_->update()
//   4. Read buffer into BMP: generate_bmp_()
//   5. Restore original page and sleep state
//   6. Re-render to put the display back: display_->update()
//   7. Signal semaphore -- HTTP task unblocks and sends the BMP

void DisplayCaptureHandler::loop() {
  if (!this->request_pending_)
    return;
  this->request_pending_ = false;

  bool was_sleeping = false;
  bool page_switched = false;

  // --- Wake display if sleeping ---
#ifdef DISPLAY_CAPTURE_USE_GLOBALS
  if (this->sleep_global_ != nullptr && this->sleep_global_->value()) {
    was_sleeping = true;
    this->sleep_global_->value() = false;
  }
#endif

  // --- Switch to requested page ---
  if (this->requested_page_ >= 0) {
    switch (this->page_mode_) {
      case NATIVE_PAGES: {
        int idx = this->requested_page_;
        if (idx >= 0 && idx < (int) this->pages_.size()) {
          // Save active page so we can restore it after capture.
          // get_active_page() returns const*, show_page() takes non-const* --
          // the const_cast in the restore path is safe because we're putting
          // back a page that was already active.
          this->saved_native_page_ = this->display_->get_active_page();
          this->display_->show_page(this->pages_[idx]);
          page_switched = true;
        }
        break;
      }
#ifdef DISPLAY_CAPTURE_USE_GLOBALS
      case GLOBAL_PAGES: {
        this->saved_global_page_ = this->page_global_->value();
        if (this->saved_global_page_ != this->requested_page_) {
          this->page_global_->value() = this->requested_page_;
          page_switched = true;
        }
        break;
      }
#endif
      default:
        break;
    }
  }

  // --- Render + capture ---
  this->display_->update();
  this->generate_bmp_();

  // --- Restore original state ---
  if (page_switched) {
    switch (this->page_mode_) {
      case NATIVE_PAGES:
        if (this->saved_native_page_ != nullptr) {
          this->display_->show_page(const_cast<display::DisplayPage *>(this->saved_native_page_));
        }
        break;
#ifdef DISPLAY_CAPTURE_USE_GLOBALS
      case GLOBAL_PAGES:
        this->page_global_->value() = this->saved_global_page_;
        break;
#endif
      default:
        break;
    }
  }

#ifdef DISPLAY_CAPTURE_USE_GLOBALS
  if (was_sleeping) {
    this->sleep_global_->value() = true;
  }
#endif

  // Re-render to put the physical display back to its original state.
  // This causes a brief (~50ms) flash of the captured page on the display.
  if (page_switched || was_sleeping) {
    this->display_->update();
  }

  // Unblock the HTTP handler -- it can now send the BMP response.
  xSemaphoreGive(this->semaphore_);
}

// ============================================================================
// HTTP handlers -- run on the web server's FreeRTOS task
// ============================================================================

/// Screenshot handler: sets a flag for the main loop and blocks until the
/// BMP is ready. The 5-second timeout prevents deadlocks if the main loop
/// is stuck or the component is misconfigured.
///
/// IMPORTANT: After req->send(), the web server may still be reading from
/// bmp_data_ asynchronously (ESPAsyncWebServer on Arduino does not copy
/// the buffer). We do NOT free the buffer here -- it is freed at the start
/// of the next generate_bmp_() call, by which time the response is
/// guaranteed to have been sent. The ~225 KB PSRAM cost between requests
/// is negligible on devices with 2-8 MB PSRAM.
void DisplayCaptureHandler::handle_screenshot_(AsyncWebServerRequest *req) {
  int requested_page = -1;
  if (req->hasParam("page")) {
    requested_page = atoi(req->arg("page").c_str());
  }

  this->requested_page_ = requested_page;
  this->request_pending_ = true;

  if (xSemaphoreTake(this->semaphore_, pdMS_TO_TICKS(5000)) == pdTRUE) {
    if (this->bmp_data_ != nullptr && this->bmp_size_ > 0) {
#ifdef USE_ESP_IDF
      auto *response = req->beginResponse_P(200, "image/bmp", this->bmp_data_, this->bmp_size_);
#else
      auto *response = req->beginResponse(200, "image/bmp", this->bmp_data_, this->bmp_size_);
#endif
      response->addHeader("Cache-Control", "no-cache");
      req->send(response);
      // Buffer is intentionally NOT freed here. See comment above.
    } else {
      req->send(500, "text/plain", "Failed to capture screenshot");
    }
  } else {
    this->request_pending_ = false;
    req->send(504, "text/plain", "Screenshot capture timed out");
  }
}

/// Info handler: returns JSON metadata about the display and page configuration.
/// Runs synchronously on the HTTP task -- all data is immutable after setup.
///
/// Response format:
///   {"pages":3,"width":320,"height":240,"mode":"native_pages","page_names":["Main","Graph","Settings"]}
void DisplayCaptureHandler::handle_info_(AsyncWebServerRequest *req) {
  int screen_w = this->display_->get_width();
  int screen_h = this->display_->get_height();
  int page_count = this->get_page_count();

  const char *mode_str = "single";
  if (this->page_mode_ == NATIVE_PAGES)
    mode_str = "native_pages";
  else if (this->page_mode_ == GLOBAL_PAGES)
    mode_str = "global_pages";

  std::string json = "{";
  json += "\"width\":" + std::to_string(screen_w);
  json += ",\"height\":" + std::to_string(screen_h);
  // Only include "pages" when the count is known (>= 0).
  // In global_pages mode without page_names, the count is unknown (-1)
  // and we omit the field so clients can distinguish "unknown" from "zero".
  if (page_count >= 0) {
    json += ",\"pages\":" + std::to_string(page_count);
  }
  json += ",\"mode\":\"";
  json += mode_str;
  json += "\"";

  if (!this->page_names_.empty()) {
    json += ",\"page_names\":[";
    for (size_t i = 0; i < this->page_names_.size(); i++) {
      if (i > 0)
        json += ",";
      json += "\"";
      for (char c : this->page_names_[i]) {
        switch (c) {
          case '"':  json += "\\\""; break;
          case '\\': json += "\\\\"; break;
          case '\n': json += "\\n"; break;
          case '\r': json += "\\r"; break;
          case '\t': json += "\\t"; break;
          case '\b': json += "\\b"; break;
          case '\f': json += "\\f"; break;
          default:
            // Escape remaining control characters (U+0000 through U+001F)
            if (static_cast<unsigned char>(c) < 0x20) {
              char buf[8];
              snprintf(buf, sizeof(buf), "\\u%04x", static_cast<unsigned char>(c));
              json += buf;
            } else {
              json += c;
            }
            break;
        }
      }
      json += "\"";
    }
    json += "]";
  }

  json += "}";

  req->send(200, "application/json", json.c_str());
}

// ============================================================================
// BMP generation -- called from loop() on the main task
// ============================================================================
//
// Reads the display's internal RGB565 framebuffer and generates a standard
// 24-bit uncompressed BMP (BITMAPINFOHEADER format) in PSRAM.
//
// Key details:
//   - Uses static_cast to access DisplayBuffer::buffer_ (dynamic_cast is
//     unavailable because ESP-IDF builds with -fno-rtti)
//   - Handles all four display rotations by applying the inverse of
//     ESPHome's draw_pixel_at() rotation transform
//   - RGB565 (2 bytes/pixel) -> 24-bit BGR (3 bytes/pixel, BMP native order)
//   - BMP rows are stored bottom-to-top, padded to 4-byte boundaries
//   - Output size for 320x240: 54 + (960 * 240) = 230,454 bytes

void DisplayCaptureHandler::generate_bmp_() {
  // Free the previous screenshot buffer. This is deferred from
  // handle_screenshot_() because the async web server may still be reading
  // from the buffer when that function returns. By the time the next request
  // reaches generate_bmp_(), the previous response is guaranteed to have
  // been fully sent (the semaphore ensures only one request at a time).
  if (this->bmp_data_ != nullptr) {
    heap_caps_free(this->bmp_data_);
    this->bmp_data_ = nullptr;
    this->bmp_size_ = 0;
  }

  // get_width()/get_height() return dimensions after rotation (what you see on screen).
  // get_native_width()/get_native_height() return the panel's physical dimensions
  // (before rotation) -- these are needed for buffer indexing.
  int screen_w = this->display_->get_width();
  int screen_h = this->display_->get_height();
  int w_int = this->display_->get_native_width();
  int h_int = this->display_->get_native_height();
  auto rotation = this->display_->get_rotation();

  // BMP row stride must be a multiple of 4 bytes
  int row_stride = ((screen_w * 3 + 3) / 4) * 4;
  uint32_t pixel_data_size = row_stride * screen_h;
  uint32_t file_size = 54 + pixel_data_size;  // 14 (file header) + 40 (DIB header) + pixels

  // Allocate in PSRAM (external SPI RAM) -- ~225 KB for 320x240.
  // Internal SRAM is only ~320 KB total and mostly used by the framework.
  this->bmp_data_ = (uint8_t *) heap_caps_malloc(file_size, MALLOC_CAP_SPIRAM);
  if (this->bmp_data_ == nullptr) {
    ESP_LOGE(TAG, "Failed to allocate %u bytes in PSRAM for BMP", file_size);
    this->bmp_size_ = 0;
    return;
  }
  this->bmp_size_ = file_size;

  memset(this->bmp_data_, 0, 54);

  // --- BMP file header (14 bytes) ---
  this->bmp_data_[0] = 'B';
  this->bmp_data_[1] = 'M';
  write_le32_(this->bmp_data_ + 2, file_size);
  write_le32_(this->bmp_data_ + 10, 54);  // offset to pixel data

  // --- DIB header (BITMAPINFOHEADER, 40 bytes) ---
  write_le32_(this->bmp_data_ + 14, 40);         // header size
  write_le32_(this->bmp_data_ + 18, screen_w);   // width
  write_le32_(this->bmp_data_ + 22, screen_h);   // height (positive = bottom-up)
  write_le16_(this->bmp_data_ + 26, 1);          // color planes
  write_le16_(this->bmp_data_ + 28, 24);         // bits per pixel
  write_le32_(this->bmp_data_ + 34, pixel_data_size);

  // --- Pixel data ---
  // Get the framebuffer pointer using the configured backend.
  uint8_t *buf = nullptr;
  if (this->backend_ == BACKEND_RPI_DPI_RGB) {
#ifdef USE_RPI_DPI_RGB
    auto *rgb_display = static_cast<rpi_dpi_rgb::RpiDpiRgb *>(this->display_);
    if (rgb_display->handle_ == nullptr) {
      ESP_LOGE(TAG, "rpi_dpi_rgb handle is null");
      heap_caps_free(this->bmp_data_);
      this->bmp_data_ = nullptr;
      this->bmp_size_ = 0;
      return;
    }
    void *fb = nullptr;
    esp_err_t err = esp_lcd_rgb_panel_get_frame_buffer(rgb_display->handle_, 1, &fb);
    if (err != ESP_OK || fb == nullptr) {
      ESP_LOGE(TAG, "Failed to get rpi_dpi_rgb frame buffer (%d)", err);
      heap_caps_free(this->bmp_data_);
      this->bmp_data_ = nullptr;
      this->bmp_size_ = 0;
      return;
    }
    buf = static_cast<uint8_t *>(fb);
#else
    ESP_LOGE(TAG, "rpi_dpi_rgb backend requested but USE_RPI_DPI_RGB is not enabled in this build");
    heap_caps_free(this->bmp_data_);
    this->bmp_data_ = nullptr;
    this->bmp_size_ = 0;
    return;
#endif
  } else {
    // Standard DisplayBuffer path (ILI9XXX, ST7789V, etc.)
    // dynamic_cast is unavailable with -fno-rtti, so we use static_cast.
    auto *display_buffer = static_cast<display::DisplayBuffer *>(this->display_);
    buf = display_buffer->buffer_;
  }

  for (int sy = 0; sy < screen_h; sy++) {
    // BMP stores rows bottom-to-top
    int bmp_row = screen_h - 1 - sy;
    uint8_t *row_ptr = this->bmp_data_ + 54 + bmp_row * row_stride;

    for (int sx = 0; sx < screen_w; sx++) {
      // Map screen coordinates (sx, sy) to buffer coordinates (bx, by).
      //
      // ESPHome's draw_pixel_at() applies a forward rotation transform when
      // writing pixels to the buffer. We need the INVERSE transform to read
      // them back in screen order:
      //
      //   Rotation | Forward (screen->buffer)       | Inverse (buffer->screen)
      //   ---------|--------------------------------|-------------------------
      //   0°       | bx=sx, by=sy                   | bx=sx, by=sy
      //   90°      | bx=w-1-y, by=x                 | bx=w-1-sy, by=sx
      //   180°     | bx=w-1-x, by=h-1-y             | bx=w-1-sx, by=h-1-sy
      //   270°     | bx=y, by=h-1-x                 | bx=sy, by=h-1-sx
      //
      // w and h here are native (pre-rotation) panel dimensions.
      int bx, by;
      switch (rotation) {
        case display::DISPLAY_ROTATION_0_DEGREES:
          bx = sx;
          by = sy;
          break;
        case display::DISPLAY_ROTATION_90_DEGREES:
          bx = w_int - 1 - sy;
          by = sx;
          break;
        case display::DISPLAY_ROTATION_180_DEGREES:
          bx = w_int - 1 - sx;
          by = h_int - 1 - sy;
          break;
        case display::DISPLAY_ROTATION_270_DEGREES:
          bx = sy;
          by = h_int - 1 - sx;
          break;
        default:
          bx = sx;
          by = sy;
          break;
      }

      // Decode RGB565 pixel (2 bytes per pixel in BITS_16 mode):
      //
      //   byte[0] = RRRRRGGG  (high byte: 5 bits red, upper 3 bits green)
      //   byte[1] = GGGBBBBB  (low byte: lower 3 bits green, 5 bits blue)
      //
      // Expand to 8-bit per channel with proper scaling (not just shifting).
      uint32_t pos = (by * w_int + bx) * 2;
      uint8_t high = buf[pos];
      uint8_t low = buf[pos + 1];

      uint8_t r5 = high >> 3;
      uint8_t g6 = ((high & 0x07) << 3) | (low >> 5);
      uint8_t b5 = low & 0x1F;
      uint8_t r = (r5 * 255) / 31;
      uint8_t g = (g6 * 255) / 63;
      uint8_t b = (b5 * 255) / 31;

      // BMP pixel order is BGR (not RGB)
      row_ptr[sx * 3 + 0] = b;
      row_ptr[sx * 3 + 1] = g;
      row_ptr[sx * 3 + 2] = r;
    }
  }

  ESP_LOGI(TAG, "Generated %dx%d BMP (%u bytes)", screen_w, screen_h, file_size);
}

}  // namespace display_capture
}  // namespace esphome
