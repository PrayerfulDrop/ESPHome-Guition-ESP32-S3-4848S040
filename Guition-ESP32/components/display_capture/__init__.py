"""
display_capture -- ESPHome external component for remote display screenshots.

Adds GET /screenshot and GET /screenshot/info HTTP endpoints to any ESP32
device with a display and web_server component. Supports three page modes:

  - Single:       No pages config -- captures current screen only
  - Native pages: pages: [page_main, page_graph, ...] -- uses ESPHome DisplayPage
  - Global pages: page_global: current_page -- uses a globals<int> for page tracking

See README.md for full documentation.
"""

import esphome.codegen as cg
from esphome.components import web_server_base, display
from esphome.components.web_server_base import CONF_WEB_SERVER_BASE_ID
import esphome.config_validation as cv
from esphome.const import CONF_ID, CONF_DISPLAY_ID

# web_server_base provides the HTTP server infrastructure (AsyncWebHandler)
AUTO_LOAD = ["web_server_base"]

# YAML config keys
CONF_PAGES = "pages"
CONF_PAGE_GLOBAL = "page_global"
CONF_SLEEP_GLOBAL = "sleep_global"
CONF_PAGE_NAMES = "page_names"
CONF_BACKEND = "backend"

BACKEND_DISPLAY_BUFFER = "display_buffer"
BACKEND_RPI_DPI_RGB = "rpi_dpi_rgb"

# C++ class references for code generation
display_capture_ns = cg.esphome_ns.namespace("display_capture")
DisplayCaptureHandler = display_capture_ns.class_(
    "DisplayCaptureHandler", cg.Component
)

# References to types from other components.
# DisplayPage: ESPHome's native page abstraction (defined in display/__init__.py)
display_ns = cg.esphome_ns.namespace("display")
DisplayPage = display_ns.class_("DisplayPage")

# GlobalsComponent: ESPHome's globals component (template class)
globals_ns = cg.esphome_ns.namespace("globals")
GlobalsComponent = globals_ns.class_("GlobalsComponent", cg.Component)

CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(): cv.declare_id(DisplayCaptureHandler),
        cv.GenerateID(CONF_WEB_SERVER_BASE_ID): cv.use_id(
            web_server_base.WebServerBase
        ),
        # Accepts any Display subclass (ILI9XXX, ST7789V, etc.)
        cv.Required(CONF_DISPLAY_ID): cv.use_id(display.Display),
        # cv.Exclusive: pages and page_global are mutually exclusive.
        # ESPHome config validation rejects YAML that specifies both.
        cv.Exclusive(CONF_PAGES, "page_mode"): cv.ensure_list(
            cv.use_id(DisplayPage)
        ),
        cv.Exclusive(CONF_PAGE_GLOBAL, "page_mode"): cv.use_id(GlobalsComponent),
        # sleep_global: temporarily wakes the display before capture
        cv.Optional(CONF_SLEEP_GLOBAL): cv.use_id(GlobalsComponent),
        # page_names: human-readable names returned by /screenshot/info
        cv.Optional(CONF_PAGE_NAMES): cv.ensure_list(cv.string),
        cv.Optional(CONF_BACKEND, default=BACKEND_DISPLAY_BUFFER): cv.one_of(
            BACKEND_DISPLAY_BUFFER, BACKEND_RPI_DPI_RGB, lower=True
        ),
    },
).extend(cv.COMPONENT_SCHEMA)


async def to_code(config):
    paren = await cg.get_variable(config[CONF_WEB_SERVER_BASE_ID])

    var = cg.new_Pvariable(config[CONF_ID], paren)
    await cg.register_component(var, config)

    disp = await cg.get_variable(config[CONF_DISPLAY_ID])
    cg.add(var.set_display(disp))
    cg.add(var.set_backend(config[CONF_BACKEND]))

    # Native pages mode: resolve each DisplayPage ID and pass as a vector
    if CONF_PAGES in config:
        pages = []
        for page_id in config[CONF_PAGES]:
            page_var = await cg.get_variable(page_id)
            pages.append(page_var)
        cg.add(var.set_pages(pages))

    # Globals support is conditionally compiled. ESPHome only includes a
    # component's headers in the build when that component is used, so the
    # globals_component.h header won't exist in builds without globals.
    # We set a C++ define so the .cpp can #ifdef around the include and code.
    if CONF_PAGE_GLOBAL in config or CONF_SLEEP_GLOBAL in config:
        cg.add_define("DISPLAY_CAPTURE_USE_GLOBALS")

    if CONF_PAGE_GLOBAL in config:
        page_global = await cg.get_variable(config[CONF_PAGE_GLOBAL])
        cg.add(var.set_page_global(page_global))

    if CONF_SLEEP_GLOBAL in config:
        sleep_global = await cg.get_variable(config[CONF_SLEEP_GLOBAL])
        cg.add(var.set_sleep_global(sleep_global))

    if CONF_PAGE_NAMES in config:
        for name in config[CONF_PAGE_NAMES]:
            cg.add(var.add_page_name(name))
