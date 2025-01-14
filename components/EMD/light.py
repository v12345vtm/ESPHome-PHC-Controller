import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import switch, light
from esphome.const import CONF_OUTPUT_ID
from ..PHCController import CONTROLLER_ID, PHCController

DEPENDENCIES = ['PHCController']

ADDRESS = 'dip'
CHANNEL = 'channel'

amd_light_ns = cg.esphome_ns.namespace('EMD_light')
EMDLight = amd_light_ns.class_(
    'EMD_light', light.LightOutput, cg.EntityBase, cg.Component)

CONFIG_SCHEMA = light.BINARY_LIGHT_SCHEMA.extend({
    cv.GenerateID(CONF_OUTPUT_ID): cv.declare_id(EMDLight),
    cv.Required(CONTROLLER_ID): cv.use_id(PHCController),
    cv.Required(ADDRESS): cv.int_range(min=0, max=31),
    cv.Required(CHANNEL): cv.int_range(min=0, max=15)
}).extend(cv.COMPONENT_SCHEMA)


def to_code(config):
    controller = yield cg.get_variable(config[CONTROLLER_ID])
    var = cg.new_Pvariable(config[CONF_OUTPUT_ID])
    yield cg.register_component(var, config)
    yield light.register_light(var, config)

    cg.add(var.set_address(config[ADDRESS]))
    cg.add(var.set_channel(config[CHANNEL]))
    cg.add(controller.register_EMDLight(var))
