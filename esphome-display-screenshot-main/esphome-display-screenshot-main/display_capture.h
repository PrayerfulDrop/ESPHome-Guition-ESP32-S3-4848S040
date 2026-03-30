// display_capture -- ESPHome external component for remote display screenshots.
//
// This header declares the DisplayCaptureHandler class using only forward
// declarations and public APIs. It compiles cleanly alongside all other
// ESPHome headers. The implementation in display_capture.cpp uses the
// #define protected public hack in its own translation unit to access
// the display buffer.
//
// See README.md for full documentation.

#pragma once

#include "esphome/components/web_server_base/web_server_base.h"
#include "esphome/core/component.h"
#include "esphome/core/log.h"

#include <freertos/FreeRTOS.h>
#include <freertos/semphr.h>

#include <string>
#include <vector>

// Forward declarations only -- full headers are included in the .cpp file.
// This avoids pulling in display_buffer.h (which has the protected buffer_
// member we need to access) and globals_component.h (which may not exist
// in builds that don't use globals).
namespace esphome {
namespace display {
class Display;
class DisplayPage;
}  // namespace display
namespace globals {
template<typename T> class GlobalsComponent;
}  // namespace globals
}  // namespace esphome

namespace esphome {
namespace display_capture {

static const char *const TAG = "display_capture";

/// How the component discovers and switches between display pages.
enum PageMode {
  SINGLE,        ///< No page switching -- capture current screen only
  NATIVE_PAGES,  ///< ESPHome DisplayPage objects -- uses show_page()/get_active_page()
  GLOBAL_PAGES,  ///< User-managed globals<int> -- sets/restores the int value
};

/// Which display backend to use for framebuffer access.
enum CaptureBackend {
  BACKEND_DISPLAY_BUFFER,  ///< Standard DisplayBuffer (ILI9XXX, ST7789V, etc.)
  BACKEND_RPI_DPI_RGB,     ///< rpi_dpi_rgb (ESP32-S3 RGB LCD panels)
};

/// HTTP handler that captures the display framebuffer as a BMP image.
///
/// Registers two endpoints on the device's existing web server:
///   GET /screenshot[?page=N]  -- returns a 24-bit BMP of the display
///   GET /screenshot/info      -- returns JSON metadata (page count, dimensions, mode)
///
/// Thread safety: the /screenshot endpoint uses a binary semaphore to hand off
/// rendering work to the main ESPHome loop, since the display buffer can only
/// be safely accessed from that task. The /info endpoint reads only immutable
/// setup-time data and runs directly on the HTTP task.
class DisplayCaptureHandler : public AsyncWebHandler, public Component {
 public:
  DisplayCaptureHandler(web_server_base::WebServerBase *base) : base_(base) {}

  // --- Configuration setters (called from generated code) ---

  void set_display(display::Display *display) { this->display_ = display; }

  void set_page_global(globals::GlobalsComponent<int> *page_global) {
    this->page_global_ = page_global;
    this->page_mode_ = GLOBAL_PAGES;
  }

  void set_sleep_global(globals::GlobalsComponent<bool> *sleep_global) {
    this->sleep_global_ = sleep_global;
  }

  void set_pages(const std::vector<display::DisplayPage *> &pages) {
    this->pages_ = pages;
    this->page_mode_ = NATIVE_PAGES;
  }

  void add_page_name(const std::string &name) { this->page_names_.push_back(name); }

  void set_backend(const std::string &backend) {
    if (backend == "rpi_dpi_rgb") {
      this->backend_ = BACKEND_RPI_DPI_RGB;
      return;
    }
    this->backend_ = BACKEND_DISPLAY_BUFFER;
  }

  // --- AsyncWebHandler interface ---

  bool canHandle(AsyncWebServerRequest *request) const override {
    if (request->method() != HTTP_GET)
      return false;
    return request->url() == "/screenshot" || request->url() == "/screenshot/info";
  }

  void handleRequest(AsyncWebServerRequest *req) override {
    if (req->url() == "/screenshot/info") {
      this->handle_info_(req);
      return;
    }
    this->handle_screenshot_(req);
  }

  // --- Component interface ---

  void setup() override;
  /// Run after WiFi but before other late components.
  float get_setup_priority() const override { return setup_priority::WIFI - 1.0f; }
  void loop() override;

  /// Returns the number of known pages (from pages list or page_names).
  int get_page_count() const;

 protected:
  /// Handles GET /screenshot -- sets request_pending_ and blocks on semaphore.
  void handle_screenshot_(AsyncWebServerRequest *req);
  /// Handles GET /screenshot/info -- returns JSON, no semaphore needed.
  void handle_info_(AsyncWebServerRequest *req);
  /// Reads the display buffer and generates a 24-bit BMP in PSRAM.
  void generate_bmp_();

  /// Write a 32-bit value in little-endian byte order (for BMP headers).
  static void write_le32_(uint8_t *p, uint32_t v) {
    p[0] = v & 0xFF;
    p[1] = (v >> 8) & 0xFF;
    p[2] = (v >> 16) & 0xFF;
    p[3] = (v >> 24) & 0xFF;
  }

  /// Write a 16-bit value in little-endian byte order (for BMP headers).
  static void write_le16_(uint8_t *p, uint16_t v) {
    p[0] = v & 0xFF;
    p[1] = (v >> 8) & 0xFF;
  }

  // --- Configuration state (set once during setup, immutable after) ---

  web_server_base::WebServerBase *base_;
  display::Display *display_{nullptr};
  globals::GlobalsComponent<int> *page_global_{nullptr};
  globals::GlobalsComponent<bool> *sleep_global_{nullptr};

  PageMode page_mode_{SINGLE};
  CaptureBackend backend_{BACKEND_DISPLAY_BUFFER};  ///< Framebuffer extraction backend
  std::vector<display::DisplayPage *> pages_;       ///< Native page pointers (NATIVE_PAGES mode)
  std::vector<std::string> page_names_;             ///< Human-readable names for /info endpoint

  // --- Per-request state (used during screenshot capture) ---

  const display::DisplayPage *saved_native_page_{nullptr};  ///< Page to restore after capture
  int saved_global_page_{0};                                ///< Global value to restore after capture

  SemaphoreHandle_t semaphore_{nullptr};   ///< Coordinates HTTP task <-> main loop handoff
  volatile bool request_pending_{false};   ///< Flag: HTTP task has a pending screenshot request
  volatile int requested_page_{-1};        ///< Which page to capture (-1 = current)
  uint8_t *bmp_data_{nullptr};             ///< PSRAM buffer holding the generated BMP
  size_t bmp_size_{0};                     ///< Size of the BMP data in bytes
};

}  // namespace display_capture
}  // namespace esphome
