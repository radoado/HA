"""Quirk for AVATTO ZWPM16-1 single-phase bidirectional Zigbee energy meter."""

from typing import Final

from zigpy.profiles import zgp, zha
from zigpy.quirks import CustomDevice
from zigpy.zcl.clusters.general import (
    Basic,
    BinaryInput,
    GreenPowerProxy,
    Groups,
    Identify,
    Ota,
    Scenes,
    Time,
)
from zigpy.zcl.clusters.homeautomation import ElectricalMeasurement
from zigpy.zcl.clusters.smartenergy import Metering

from zhaquirks.const import (
    DEVICE_TYPE,
    ENDPOINTS,
    INPUT_CLUSTERS,
    MODELS_INFO,
    OUTPUT_CLUSTERS,
    PROFILE_ID,
)
from zhaquirks.tuya import TuyaLocalCluster
from zhaquirks.tuya.mcu import DPToAttributeMapping, TuyaMCUCluster

# Tuya DP constants
TUYA_DP_CURRENT: Final = 18       # Current in mA
TUYA_DP_POWER: Final = 19         # Active power in 0.1 W
TUYA_DP_VOLTAGE: Final = 20       # Voltage in 0.1 V
TUYA_DP_FLOW_DIRECTION: Final = 103  # Energy direction: 1=Export, 2=Import
TUYA_DP_TOTAL_ENERGY: Final = 104    # Total delivered energy in Wh


class AvattoElectricalMeasurement(TuyaLocalCluster, ElectricalMeasurement):
    """Cluster translating Tuya DP voltage, current, and active power into ZCL ElectricalMeasurement."""

    cluster_id = ElectricalMeasurement.cluster_id

    _CONSTANT_ATTRIBUTES = {
        # Measurement type 0x0009: Active measurement, single phase AC (Phase A)
        ElectricalMeasurement.AttributeDefs.measurement_type.id: 0x0009,
        ElectricalMeasurement.AttributeDefs.ac_voltage_multiplier.id: 1,
        ElectricalMeasurement.AttributeDefs.ac_voltage_divisor.id: 10,     # e.g. 2351 -> 235.1 V
        ElectricalMeasurement.AttributeDefs.ac_current_multiplier.id: 1,
        ElectricalMeasurement.AttributeDefs.ac_current_divisor.id: 1000,   # e.g. 3867 mA -> 3.867 A
        ElectricalMeasurement.AttributeDefs.ac_power_multiplier.id: 1,
        ElectricalMeasurement.AttributeDefs.ac_power_divisor.id: 10,       # e.g. 9002 -> 900.2 W
    }


class AvattoMetering(TuyaLocalCluster, Metering):
    """Cluster translating Tuya DP cumulative energy into ZCL Smart Energy Metering."""

    cluster_id = Metering.cluster_id

    _CONSTANT_ATTRIBUTES = {
        Metering.AttributeDefs.status.id: 0x00,
        Metering.AttributeDefs.unit_of_measure.id: 0,          # 0 = Kilowatt-hours (kWh)
        Metering.AttributeDefs.metering_device_type.id: 0,     # 0 = Electric metering
        Metering.AttributeDefs.multiplier.id: 1,
        Metering.AttributeDefs.divisor.id: 1000,              # Raw unit is Wh: 1000 Wh = 1.000 kWh
        Metering.AttributeDefs.summation_formatting.id: 0x2A,  # Display format configuration
    }


class AvattoPowerDirection(TuyaLocalCluster, BinaryInput):
    """Virtual BinaryInput cluster reporting energy flow direction (Import vs Export)."""

    cluster_id = BinaryInput.cluster_id

    _CONSTANT_ATTRIBUTES = {
        BinaryInput.AttributeDefs.description.id: "Power Flow Direction",
        BinaryInput.AttributeDefs.active_text.id: "Export (Generation)",
        BinaryInput.AttributeDefs.inactive_text.id: "Import (Consumption)",
    }


class AvattoManufCluster(TuyaMCUCluster):
    """Manufacturer-specific cluster dispatching Tuya MCU datapoints to standard clusters."""

    dp_to_attribute: dict[int, DPToAttributeMapping] = {
        TUYA_DP_CURRENT: DPToAttributeMapping(
            AvattoElectricalMeasurement.ep_attribute,
            "rms_current",
        ),
        TUYA_DP_POWER: DPToAttributeMapping(
            AvattoElectricalMeasurement.ep_attribute,
            "active_power",
        ),
        TUYA_DP_VOLTAGE: DPToAttributeMapping(
            AvattoElectricalMeasurement.ep_attribute,
            "rms_voltage",
        ),
        TUYA_DP_FLOW_DIRECTION: DPToAttributeMapping(
            AvattoPowerDirection.ep_attribute,
            "present_value",
            # DP 103 enum: 2 = grid consumption (False/off), 1 = grid export (True/on)
            converter=lambda val: bool(val != 2),
        ),
        TUYA_DP_TOTAL_ENERGY: DPToAttributeMapping(
            AvattoMetering.ep_attribute,
            "current_summ_delivered",
        ),
    }

    data_point_handlers = {
        TUYA_DP_CURRENT: "_dp_2_attr_update",
        TUYA_DP_POWER: "_dp_2_attr_update",
        TUYA_DP_VOLTAGE: "_dp_2_attr_update",
        TUYA_DP_FLOW_DIRECTION: "_dp_2_attr_update",
        TUYA_DP_TOTAL_ENERGY: "_dp_2_attr_update",
    }


class AvattoEnergyMeterZWPM16(CustomDevice):
    """Quirk for AVATTO ZWPM16-1 bidirectional energy monitor."""

    signature = {
        MODELS_INFO: [
            ("_TZE28C1000000_goecjd1t", "TS0601"),
            ("_TZE204_goecjd1t", "TS0601"),
        ],
        ENDPOINTS: {
            # Endpoint 1: Main metering and control endpoint
            1: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.SMART_PLUG,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    Identify.cluster_id,
                    Groups.cluster_id,
                    Scenes.cluster_id,
                    TuyaMCUCluster.cluster_id,
                    0xE000,
                    0xEB00,
                    0xED00,
                ],
                OUTPUT_CLUSTERS: [
                    Time.cluster_id,
                    Ota.cluster_id,
                ],
            },
            # Endpoint 242: Green Power Proxy
            242: {
                PROFILE_ID: zgp.PROFILE_ID,
                DEVICE_TYPE: zgp.DeviceType.PROXY_BASIC,
                INPUT_CLUSTERS: [],
                OUTPUT_CLUSTERS: [
                    GreenPowerProxy.cluster_id,
                ],
            },
        },
    }

    replacement = {
        ENDPOINTS: {
            1: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.SMART_PLUG,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    Identify.cluster_id,
                    Groups.cluster_id,
                    Scenes.cluster_id,
                    AvattoManufCluster,
                    AvattoElectricalMeasurement,
                    AvattoMetering,
                    AvattoPowerDirection,
                ],
                OUTPUT_CLUSTERS: [
                    Time.cluster_id,
                    Ota.cluster_id,
                ],
            },
            242: {
                PROFILE_ID: zgp.PROFILE_ID,
                DEVICE_TYPE: zgp.DeviceType.PROXY_BASIC,
                INPUT_CLUSTERS: [],
                OUTPUT_CLUSTERS: [
                    GreenPowerProxy.cluster_id,
                ],
            },
        }
    }
