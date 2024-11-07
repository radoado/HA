from zigpy.profiles import zha
from zigpy.quirks import CustomDevice
from zigpy.zcl.clusters.general import Basic, Identify, OnOff, Scenes, Groups, Time, Ota
from zhaquirks.const import (
    MODELS_INFO,
    ENDPOINTS,
    INPUT_CLUSTERS,
    OUTPUT_CLUSTERS,
    PROFILE_ID,
    DEVICE_TYPE,
    SKIP_CONFIGURATION,
)
from zhaquirks.tuya import (
    EnchantedDevice,
    TuyaSwitch,
    TuyaZBE000Cluster,
    TuyaZBExternalSwitchTypeCluster,
    TuyaZBOnOffAttributeCluster,
)
from zhaquirks.tuya.mcu import EnchantedDevice

class TS0012(EnchantedDevice, TuyaSwitch):
    """Tuya TS0012 double switch device."""

    signature = {
        MODELS_INFO: [("_TZ3000_s8r1qoyq", "TS0012")],
        ENDPOINTS: {
            1: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.ON_OFF_LIGHT,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    Identify.cluster_id,
                    Groups.cluster_id,
                    Scenes.cluster_id,
                    OnOff.cluster_id,
                    ],
                OUTPUT_CLUSTERS: [Ota.cluster_id, Time.cluster_id],
            },
            2: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.ON_OFF_LIGHT,
                INPUT_CLUSTERS: [
                    Identify.cluster_id,
                    Groups.cluster_id,
                    Scenes.cluster_id,
                    OnOff.cluster_id,
                    ],
                OUTPUT_CLUSTERS: [],
            },
        },
    }

    replacement = {
        ENDPOINTS: {
            1: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.ON_OFF_LIGHT,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    Identify.cluster_id,
                    Groups.cluster_id,
                    Scenes.cluster_id,
                    TuyaZBOnOffAttributeCluster,
                    ],
                OUTPUT_CLUSTERS: [Time.cluster_id, Ota.cluster_id],
            },
            2: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.ON_OFF_LIGHT,
                INPUT_CLUSTERS: [
                    Identify.cluster_id,
                    Groups.cluster_id,
                    Scenes.cluster_id,
                    TuyaZBOnOffAttributeCluster,
                    ],
                OUTPUT_CLUSTERS: [],
            },
        }
    }
