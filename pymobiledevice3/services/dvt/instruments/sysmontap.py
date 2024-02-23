import dataclasses

from pymobiledevice3.services.dvt.instruments.device_info import DeviceInfo
from pymobiledevice3.services.remote_server import Tap
import logging

logger = logging.getLogger(__name__)


class Sysmontap(Tap):
    IDENTIFIER = 'com.apple.instruments.server.services.sysmontap'

    def __init__(self, dvt):
        self._device_info = DeviceInfo(dvt)

        process_attributes = list(self._device_info.request_information('sysmonProcessAttributes'))
        system_attributes = list(self._device_info.request_information('sysmonSystemAttributes'))

        self.process_attributes_cls = dataclasses.make_dataclass('SysmonProcessAttributes', process_attributes)
        self.system_attributes_cls = dataclasses.make_dataclass('SysmonSystemAttributes', system_attributes)


        config = {
            'ur': 1000,  # Output frequency ms
            'bm': 0,
            'procAttrs': process_attributes,
            'sysAttrs': system_attributes,
            'cpuUsage': True,
            'sampleInterval': 1000000000
        }

        super().__init__(dvt, self.IDENTIFIER, config)

    def __iter__(self):
        while True:
            yield from self.channel.receive_plist()

    def iter_processes(self):
        for row in self:
            #logger.info(row)
            if 'Processes' not in row:
                continue

            entries = []
            processes = row['Processes'].items()
            for pid, process_info in processes:
                entry = dataclasses.asdict(self.process_attributes_cls(*process_info))
                entries.append(entry)


            yield entries

    def iter_sysandproc(self):
        #entries = []
        for row in self:
            entries = []
            #logger.info('---------------------')
            #logger.info(type(row))
            #logger.info('---------------------')
            #if isinstance(row, str):
            #    logger.info(row)
            if isinstance(row, dict) and 'Processes' in row:
                ProcessEndMachAbsTime = row['EndMachAbsTime']
                ProcessStartMachAbsTime =row['StartMachAbsTime']
                logger.debug(f'ProcessEndMachAbsTime:{ProcessEndMachAbsTime}')
                logger.debug(f'ProcessStartMachAbsTime:{ProcessStartMachAbsTime}')
                processes = row['Processes'].items()
                for pid, process_info in processes:
                    entry = dataclasses.asdict(self.process_attributes_cls(*process_info))
                    entries.append(entry)
            elif isinstance(row, dict) and 'SystemCPUUsage' in row and 'CPUCount' in row:
                SysEndMachAbsTime = row['EndMachAbsTime']
                SysStartMachAbsTime =row['StartMachAbsTime']
                logger.debug(f'SysEndMachAbsTime:{SysEndMachAbsTime}')
                logger.debug(f'SysStartMachAbsTime:{SysStartMachAbsTime}')
                logger.debug(f'SystemRow:{row}')
                entries.append(row)
            #elif isinstance(row, str) and row=='k':
            #    yield entries
            #    #logger.info(row)
            #    logger.info(len(entries))
            #    entries = []
            yield entries
