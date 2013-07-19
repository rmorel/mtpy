# -*- coding: utf-8 -*-
"""
====================
zonge
====================

    * Tools for interfacing with MTFT24
    * Tools for interfacing with MTEdit
    
    
Created on Tue Jul 11 10:53:23 2013

@author: jpeacock-pr
"""

#==============================================================================

import numpy as np
import time
import os
import shutil
import mtpy.core.z as mtz
import mtpy.utils.format as MTft
import mtpy.utils.configfile as mtcf
import mtpy.core.edi as mtedi
import mtpy.usgs.zen as zen

#==============================================================================
datetime_fmt = '%Y-%m-%d,%H:%M:%S'

#==============================================================================
# class for  mtft24
#==============================================================================
class ZongeMTFT():
    """
    Reads and writes config files for MTFT24 version 1.10
    
    
    ========================= =================================================
    Attributes                Description
    ========================= =================================================
    
    
    ========================= =================================================
    """
    def __init__(self):
        
        #--> standard MTFT meta data
        self.MTFT_Version = '1.10v'
        self.MTFT_MHAFreq = 3
        self.MTFT_WindowTaper = '4 Pi Prolate'
        self.MTFT_WindowLength = 64
        self.MTFT_WindowOverlap = 48
        self.MTFT_NDecFlt = 5
        self.MTFT_PWFilter = 'Auto-Regression'
        self.MTFT_NPWCoef = 5
        self.MTFT_DeTrend = 'Yes'
        self.MTFT_T0OffsetMax = 1.5
        self.MTFT_Despike = 'Yes'
        self.MTFT_SpikePnt = 1
        self.MTFT_SpikeDev = 4
        self.MTFT_NotchFlt = 'Yes'
        self.MTFT_NotchFrq =  list(np.arange(60, 600, 60))
        self.MTFT_NotchWidth = range(1,len(self.MTFT_NotchFrq)+1)
        self.MTFT_StackFlt = 'No'
        self.MTFT_StackTaper = 'Yes'
        self.MTFT_StackFrq = [60,1808,4960]
        self.MTFT_SysCal = 'Yes'
        self.MTFT_BandFrq = [32, 256, 512, 1024, 2048, 4096, 32768] 
        self.MTFT_BandFrqMin = [7.31000E-4, 7.31000E-4, 7.31000E-4, 0.25, 0.25, 
                                0.25, 1]
        self.MTFT_BandFrqMax = [10, 80, 160, 320, 640, 1280, 10240]
        self.MTFT_TSPlot_PntRange = 4096
        self.MTFT_TSPlot_ChnRange = '1000'+',1000'*17 
        
        #--> time series meta data
        self.TS_Number = 3
        self.TS_FrqBand = [32, 256, 512]
        self.TS_T0Offset = [0, 0, 0]
        self.TS_T0Error = [0, 0, 0]

        #--> setup parameters
        self.Setup_Number = 1
        self.Setup_ID = 1
        self.Setup_Use = 'Yes'
        self.setup_lst = []

        #--> survey parameters
        self.Unit_Length = 'm'
        self.Chn_Cmp = ['Hx', 'Hy', 'Hz', 'Ex', 'Ey']
        self.Chn_ID = ['2314', '2324', '2334', '4', '5']
        self.Chn_Gain = [1, 1, 1, 1, 1]
        self.Chn_Length = [100]*5
        self.Chn_dict = dict([(chkey, [cid, cg, cl]) for chkey, cid, cg, cl in 
                               zip(self.Chn_Cmp, self.Chn_ID, self.Chn_Gain,
                                   self.Chn_Length)])
                                   
        self.Chn_Cmp_lst = []
        self.num_comp = len(self.Chn_Cmp)
        self.Ant_FrqMin = 7.31E-4
        self.Ant_FrqMax = 10240
        self.Rx_HPR = [90, 0, 0]
        self.Remote_Component = 'Hx,Hy'
        self.Remote_Rotation = 0
        self.Remote_Path = ''
        self.cache_path = None
        
        #info dict
        self.ts_info_keys = ['File#', 'Setup', 'SkipWgt', 'LocalFile', 
                             'RemoteFile', 'LocalBlock', 'RemoteBlock', 
                             'LocalByte', 'RemoteByte', 'Date', 'Time0', 
                             'T0Offset', 'ADFrequency', 'NLocalPnt',
                             'NRemotePnt', 'ChnGain1', 'ChnGain2', 'ChnGain3',
                             'ChnGain4', 'ChnGain5']
        self.ts_info_lst = []
                             
        self.meta_keys = ['MTFT.Version', 
                          'MTFT.MHAFreq',
                          'MTFT.WindowTaper',
                          'MTFT.WindowLength',
                          'MTFT.WindowOverlap', 
                          'MTFT.NDecFlt',
                          'MTFT.PWFilter',
                          'MTFT.NPWCoef',
                          'MTFT.DeTrend', 
                          'MTFT.T0OffsetMax',
                          'MTFT.Despike',
                          'MTFT.SpikePnt',
                          'MTFT.SpikeDev',
                          'MTFT.NotchFlt',
                          'MTFT.NotchFrq',
                          'MTFT.NotchWidth',
                          'MTFT.StackFlt',
                          'MTFT.StackTaper',
                          'MTFT.StackFrq',
                          'MTFT.SysCal',
                          'MTFT.BandFrq',
                          'MTFT.BandFrqMin',
                          'MTFT.BandFrqMax',
                          'MTFT.TSPlot.PntRange',
                          'MTFT.TSPlot.ChnRange',
                          'Setup.Number',
                          'TS.Number',
                          'TS.FrqBand',
                          'TS.T0Offset',
                          'TS.T0Error',
                          'setup_lst']
                          
        self.setup_keys = ['Setup.ID',
                           'Setup.Use',
                           'Unit.Length',
                           'Chn.Cmp',
                           'Chn.ID',
                           'Chn.Length',
                           'Chn.Gain',
                           'Ant.FrqMin',
                           'Ant.FrqMax',
                           'Rx.HPR',
                           'Remote.Component',
                           'Remote.Rotation',
                           'Remote.Path']
                          
        self.value_lst = []
        self.make_value_dict()
        self.meta_dict = None
        
        self.rr_tdiff_dict = {'256':'060000', '1024':'002000', '4096':'000500'}
        
     
    def make_value_dict(self):
        self.value_lst = [self.MTFT_Version, 
                          self.MTFT_MHAFreq, 
                          self.MTFT_WindowTaper,   
                          self.MTFT_WindowLength,
                          self.MTFT_WindowOverlap,    
                          self.MTFT_NDecFlt, 
                          self.MTFT_PWFilter, 
                          self.MTFT_NPWCoef,   
                          self.MTFT_DeTrend, 
                          self.MTFT_T0OffsetMax,
                          self.MTFT_Despike,   
                          self.MTFT_SpikePnt, 
                          self.MTFT_SpikeDev,
                          self.MTFT_NotchFlt,  
                          self.MTFT_NotchFrq, 
                          self.MTFT_NotchWidth, 
                          self.MTFT_StackFlt,  
                          self.MTFT_StackTaper,
                          self.MTFT_StackFrq,
                          self.MTFT_SysCal,
                          self.MTFT_BandFrq,
                          self.MTFT_BandFrqMin,  
                          self.MTFT_BandFrqMax, 
                          self.MTFT_TSPlot_PntRange,  
                          self.MTFT_TSPlot_ChnRange,
                          self.Setup_Number,  
                          self.TS_Number, 
                          self.TS_FrqBand, 
                          self.TS_T0Offset, 
                          self.TS_T0Error,  
                          self.setup_lst]
                          
        self.meta_dict = dict([(mkey, mvalue) for mkey, mvalue in
                               zip(self.meta_keys, self.value_lst)])
                               
    def set_values(self):
        """
        from values in meta dict set attribute values
        
        """
        self.MTFT_Version = self.meta_dict['MTFT.Version']
        self.MTFT_MHAFreq = self.meta_dict['MTFT.MHAFreq'] 
        self.MTFT_WindowTaper = self.meta_dict['MTFT.WindowTaper']   
        self.MTFT_WindowLength = self.meta_dict['MTFT.WindowLength']
        self.MTFT_WindowOverlap = self.meta_dict['MTFT.WindowOverlap']    
        self.MTFT_NDecFlt = self.meta_dict['MTFT.NDecFlt'] 
        self.MTFT_PWFilter = self.meta_dict['MTFT.PWFilter'] 
        self.MTFT_NPWCoef = self.meta_dict['MTFT.NPWCoef']   
        self.MTFT_DeTrend = self.meta_dict['MTFT.DeTrend'] 
        self.MTFT_T0OffsetMax = self.meta_dict['MTFT.T0OffsetMax']
        self.MTFT_Despike = self.meta_dict['MTFT.Despike']   
        self.MTFT_SpikePnt = self.meta_dict['MTFT.SpikePnt'] 
        self.MTFT_SpikeDev = self.meta_dict['MTFT.SpikeDev']
        self.MTFT_NotchFlt = self.meta_dict['MTFT.NotchFlt']  
        self.MTFT_NotchFrq = self.meta_dict['MTFT.NotchFrq'] 
        self.MTFT_NotchWidth = self.meta_dict['MTFT.NotchWidth'] 
        self.MTFT_StackFlt = self.meta_dict['MTFT.StackFlt']  
        self.MTFT_StackTaper = self.meta_dict['MTFT.StackTaper']
        self.MTFT_StackFrq = self.meta_dict['MTFT.StackFrq']
        self.MTFT_SysCal = self.meta_dict['MTFT.SysCal']
        self.MTFT_BandFrq = self.meta_dict['MTFT.BandFrq']
        self.MTFT_BandFrqMin = self.meta_dict['MTFT.BandFrqMin']  
        self.MTFT_BandFrqMax = self.meta_dict['MTFT.BandFrqMax'] 
        self.MTFT_TSPlot_PntRange = self.meta_dict['MTFT.TSPlot.PntRange']  
        self.MTFT_TSPlot_ChnRange = self.meta_dict['MTFT.TSPlot.ChnRange']
        self.Setup_Number = self.meta_dict['Setup.Number']  
        self.TS_Number = self.meta_dict['TS.Number'] 
        self.TS_FrqBand = self.meta_dict['TS.FrqBand'] 
        self.TS_T0Offset = self.meta_dict['TS.T0Offset'] 
        self.TS_T0Error = self.meta_dict['TS.T0Error']  
        self.setup_lst = self.meta_dict['setup_lst']
    
    def sort_ts_lst(self):
        """
        sort the time series list such that all the same sampling rates are
        in sequential order, this needs to be done to get reasonable 
        coefficients out of mtft
        """
        
        if self.ts_info_lst == []:
            return
        
        new_ts_lst = sorted(self.ts_info_lst, key=lambda k: k['ADFrequency'])
        
        for ii, new_ts in enumerate(new_ts_lst, 1):
            new_ts['File#'] = ii
            for tkey in self.ts_info_keys:
                if not type(new_ts[tkey]) is str:
                    new_ts[tkey] = str(new_ts[tkey])
                    
        self.ts_info_lst = new_ts_lst
        
    def get_rr_ts(self, ts_info_lst, remote_path=None):
        """
        get remote reference time series such that it has the same starting
        time and number of points as the collected time series
        
        Arguments:
        ----------
            **ts_info_lst** : list of dictionaries that relate to the time 
                              series to be processed.
            
            **remote_path** : directory path of merged cache files to use as
                              a remote reference.
        
        """

        if remote_path is not None:
            self.Remote_Path = remote_path
            
        if self.Remote_Path is None or self.Remote_Path == '':
            return 
            
        new_ts_info_lst = []  
        rrfnlst = [rrfn for rrfn in os.listdir(self.Remote_Path) 
                   if rrfn.find('.cac')>0]
                       
        for ts_dict in ts_info_lst:
            local_fn_lst = os.path.splitext(ts_dict['LocalFile'])[0].split('_')
            tdiff = self.rr_tdiff_dict[local_fn_lst[3]]
            
            rrfind = False
            #look backwards because if a new file was already created it will
            #be found before the original file
            for rrfn in rrfnlst[::-1]:
                rrfn_lst = os.path.splitext(rrfn)[0].split('_')
                if local_fn_lst[1] == rrfn_lst[1] and \
                   local_fn_lst[3] == rrfn_lst[3]:
                    if local_fn_lst[2] == rrfn_lst[2]:
                        zcrr = zen.ZenCache()
                        zcrr.read_cache_metadata(os.path.join(self.Remote_Path,
                                                              rrfn))
                        if int(zcrr.meta_data['TS.NPNT'][0]) == ts_dict['NLocalPnt']:
                            ts_dict['RemoteFile'] = rrfn
                            ts_dict['RemoteBlock'] = ts_dict['LocalBlock']
                            ts_dict['RemoteByte'] = ts_dict['LocalByte']
                            ts_dict['NRemotePnt'] = ts_dict['NLocalPnt']
                            for ii in range(self.num_comp+1,
                                            self.num_comp+3):
                                ts_dict['ChnGain{0}'.format(ii)] = '1'
                            new_ts_info_lst.append(ts_dict)
                            rrfind = True
                            break
                        
                        #if time series is longer than remote reference
                        elif int(zcrr.meta_data['TS.NPNT'][0]) < ts_dict['NLocalPnt']:
                            zcl = zen.ZenCache()
                            zcl.read_cache(os.path.join(self.cache_path, 
                                                        ts_dict['LocalFile']))
                            zcl.ts = np.resize(zcl.ts, 
                                               (int(zcrr.meta_data['TS.NPNT'][0]),
                                                zcl.ts.shape[1]))
                            zcl.meta_data['TS.NPNT'] = [str(zcl.ts.shape[0])]
                            zcl.rewrite_cache_file()
                            
                            print 'Resized TS in {0} to {1}'.format(
                                    os.path.join(self.cache_path, 
                                                 ts_dict['LocalFile']),
                                    zcl.ts.shape)
                                    
                            ts_dict['LocalFile'] = \
                                              os.path.basename(zcl.save_fn_rw)
                            ts_dict['RemoteFile'] = rrfn
                            ts_dict['RemoteBlock'] = ts_dict['LocalBlock']
                            ts_dict['RemoteByte'] = ts_dict['LocalByte']
                            ts_dict['NLocalPnt'] = zcl.ts.shape[0]
                            ts_dict['NRemotePnt'] = ts_dict['NLocalPnt']
                            for ii in range(self.num_comp+1,
                                            self.num_comp+3):
                                ts_dict['ChnGain{0}'.format(ii)] = '1'
                            new_ts_info_lst.append(ts_dict)
                            rrfind = True
                            break
                                                        
                        #if remote reference is longer than time series
                        elif int(zcrr.meta_data['TS.NPNT'][0]) > ts_dict['NLocalPnt']:
                            zcl = zen.ZenCache()
                            zcl.read_cache_metadata(os.path.join(self.cache_path, 
                                                        ts_dict['LocalFile']))
                            
                            zcrr.read_cache(os.path.join(self.Remote_Path,
                                                         rrfn))

                            zcrr.ts = np.resize(zcrr.ts, 
                                                (ts_dict['NLocalPnt'],2))
                                                
                            zcrr.meta_data['TS.NPNT'] = [str(zcrr.ts.shape[0])]
                            zcrr.rewrite_cache_file()
                            
                            print 'Resized RR_TS in {0} to {1}'.format(
                                           os.path.join(self.Remote_Path,rrfn),
                                           zcrr.ts.shape)
                            ts_dict['RemoteFile'] = \
                                            os.path.basename(zcrr.save_fn_rw)
                            ts_dict['RemoteBlock'] = ts_dict['LocalBlock']
                            ts_dict['RemoteByte'] = ts_dict['LocalByte']
                            ts_dict['NRemotePnt'] = ts_dict['NLocalPnt']
                            for ii in range(self.num_comp+1,
                                            self.num_comp+3):
                                ts_dict['ChnGain{0}'.format(ii)] = '1'
                            new_ts_info_lst.append(ts_dict)
                            rrfind = True
                            break
                            
                    #if the starting time is different
                    elif abs(int(local_fn_lst[2])-int(rrfn_lst[2])) < int(tdiff):
                        zcl = zen.ZenCache()
                        zcl.read_cache_metadata(os.path.join(self.cache_path,
                                                        ts_dict['LocalFile']))
                                                        
                        zcrr = zen.ZenCache()
                        zcrr.read_cache_metadata(os.path.join(self.Remote_Path,
                                                     rrfn))
                        
                        if int(zcl.meta_data['TS.NPNT'][0]) != \
                           int(zcrr.meta_data['TS.NPNT'][0]):
                            local_hour = int(local_fn_lst[2][0:2])
                            local_minute = int(local_fn_lst[2][2:4])
                            local_second = int(local_fn_lst[2][4:])
                            
                            rr_hour = int(rrfn_lst[2][0:2])
                            rr_minute = int(rrfn_lst[2][2:4])
                            rr_second = int(rrfn_lst[2][4:])
                            
                            hour_diff = (rr_hour-local_hour)*3600
                            minute_diff = (rr_minute-local_minute)*60
                            second_diff = rr_second-local_second
                            
                            time_diff = abs(hour_diff+minute_diff+second_diff)
                            skip_points = int(local_fn_lst[3])*time_diff
                            
                            print ('Time difference is {0} seconds'.format(
                                                                time_diff))
                            print 'Skipping {0} points in {1}'.format(
                                                skip_points,
                                                os.path.join(self.Remote_Path,
                                                             rrfn))
                            
                            zcrr.read_cache(os.path.join(self.Remote_Path,
                                                         rrfn))
                            #resize remote reference
                            new_rr_ts = zcrr.ts[skip_points:,:]
                            
                            zcrr.ts = new_rr_ts
                            zcrr.meta_data['TS.NPNT'] = [str(zcrr.ts.shape[0])]
                            
                            zcrr.rewrite_cache_file()
                            
                            print 'Resized RR_TS in {0} to {1}'.format(
                                   os.path.join(self.cache_path, rrfn),
                                   zcrr.ts.shape)
                                   
                            ts_dict['RemoteFile'] = \
                                                os.path.basename(zcrr.save_fn_rw)
                            ts_dict['RemoteBlock'] = ts_dict['LocalBlock']
                            ts_dict['RemoteByte'] = ts_dict['LocalByte']
                            ts_dict['NRemotePnt'] = ts_dict['NLocalPnt']
                            for ii in range(self.num_comp+1,
                                            self.num_comp+3):
                                ts_dict['ChnGain{0}'.format(ii)] = '1'
                            new_ts_info_lst.append(ts_dict)
                            rrfind = True
                            break
                        else:
                            ts_dict['RemoteFile'] = \
                                                os.path.basename(zcrr.save_fn)
                            ts_dict['RemoteBlock'] = ts_dict['LocalBlock']
                            ts_dict['RemoteByte'] = ts_dict['LocalByte']
                            ts_dict['NRemotePnt'] = ts_dict['NLocalPnt']
                            for ii in range(self.num_comp+1,
                                            self.num_comp+3):
                                ts_dict['ChnGain{0}'.format(ii)] = '1'
                            new_ts_info_lst.append(ts_dict)
                            rrfind = True
                            break
                        
            if rrfind == False:
                print ('Did not find remote reference time series '
                       'for {0}'.format(ts_dict['LocalFile']))
                       
                new_ts_info_lst.append(ts_dict)
                        
        self.ts_info_lst = new_ts_info_lst
        
    def get_ts_info_lst(self, cache_path):
        """
        get information about time series and put it into dictionaries with
        keys according to header line in .cfg file
        
        Arguments:
        -----------
            **cache_path** : directory to cache files that are to be processed
        
        """

        #--> get .cac files and read meta data
        cc = 0
        
        self.cache_path = cache_path
        
        if len(self.ts_info_lst) == 0:
            for cfn in os.listdir(cache_path):
                if cfn[-4:] == '.cac' and cfn.find('$') == -1:
                    zc = zen.ZenCache()
                    zc.read_cache_metadata(os.path.join(cache_path, cfn))
                    self.Chn_Cmp_lst.append([md.capitalize() 
                                    for md in zc.meta_data['CH.CMP']
                                    if md.capitalize() in self.Chn_Cmp])
                    
                    info_dict = dict([(key, []) for key in self.ts_info_keys])
                    #put metadata information into info dict
                    info_dict['File#'] = cc+1
                    info_dict['Setup'] = 1
                    info_dict['SkipWgt'] = 1
                    info_dict['LocalFile'] = cfn
                    info_dict['RemoteFile'] = ''
                    info_dict['LocalBlock'] = cc
                    info_dict['RemoteBlock'] = ''
                    info_dict['LocalByte'] = 65
                    info_dict['RemoteByte'] = ''
                    try:
                        info_dict['Date'] = zc.meta_data['DATA.DATE0'][0]
                    except KeyError:
                        info_dict['Date'] = zc.meta_data['DATE0'][0]
                    if info_dict['Date'].find('/') >= 0:
                        dlst = info_dict['Date'].split('/')
                        info_dict['Date'] = '20{0}-{1}-{2}'.format(dlst[2], 
                                                                   dlst[0],
                                                                   dlst[1])
                    info_dict['Time0'] = '0'
                    #try:
                    #    info_dict['Time0'] = zc.meta_data['Data.Time0'][0]
                    #except KeyError:
                    #    info_dict['Time0'] = zc.meta_data['TIMEO'][0]
                    info_dict['T0Offset'] = '0'
                    info_dict['ADFrequency'] = int(zc.meta_data['TS.ADFREQ'][0])
                    info_dict['NLocalPnt'] = int(zc.meta_data['TS.NPNT'][0])
                    info_dict['NRemotePnt'] = ''
                    for ii in range(1,self.num_comp+1):
                        info_dict['ChnGain{0}'.format(ii)] = '1'               
                    
                    cc += 1
                    self.ts_info_lst.append(info_dict)
    
    def compute_number_of_setups(self):
        """
        get number of setups and set all the necessary values
        
        **Need to match setups with time series info**
        
        """
        self.setup_lst = []
        len_lst = []
        ii = 1
        for cc in self.Chn_Cmp_lst:
            comp_num = len(cc)
            if comp_num not in len_lst:
                len_lst.append(comp_num)
                setup_dict = {}
                setup_dict['Setup.ID'] = ii
                setup_dict['Setup.Use'] = 'Yes'
                setup_dict['Unit.Length'] = 'm'
                setup_dict['Chn.Cmp'] = cc
                setup_dict['Chn.ID'] = range(1,comp_num+1)
                setup_dict['Chn.Length'] = [100]*len(cc)
                setup_dict['Chn.Gain'] = [1]*len(cc)
                setup_dict['Ant.FrqMin'] = self.Ant_FrqMin
                setup_dict['Ant.FrqMax'] = self.Ant_FrqMax
                setup_dict['Rx.HPR'] = self.Rx_HPR
                setup_dict['Remote.Component'] = self.Remote_Component
                setup_dict['Remote.Rotation'] = self.Remote_Rotation
                setup_dict['Remote.Path'] = self.Remote_Path
                setup_dict['chn_dict'] = dict([(chkey, [cid, cg, cl]) 
                                                for chkey, cid, cg, cl in 
                                                zip(setup_dict['Chn.Cmp'],
                                                    setup_dict['Chn.ID'],
                                                    setup_dict['Chn.Gain'],
                                                    setup_dict['Chn.Length'])])
                ts_key_skip = len(self.ts_info_keys)-(5-len(cc)) 
                setup_dict['ts_info_keys'] = self.ts_info_keys[:ts_key_skip]
                self.setup_lst.append(setup_dict)
                ii += 1
        self.Setup_Number = len(self.setup_lst)
                
    def set_remote_reference_info(self, remote_path):
        """
        set the remote reference information in ts_info_lst
        
        Arguments:
        ----------
            **remote_path** : directory of remote reference cache files
            
        """
        
        if remote_path is None:
            return
        
        self.Remote_Path = remote_path
        for setup_dict in self.setup_lst:
            setup_dict['Chn.Cmp'] += ['Hxr', 'Hyr']
            setup_dict['Chn.ID'] += ['2284', '2274']
            setup_dict['Chn.Length'] += [100]*2
            setup_dict['Chn.Gain'] += [1]*2
            setup_dict['Ant.FrqMin'] = self.Ant_FrqMin
            setup_dict['Ant.FrqMax'] = self.Ant_FrqMax
            setup_dict['Rx.HPR'] = self.Rx_HPR
            setup_dict['Remote.Component'] = self.Remote_Component
            setup_dict['Remote.Rotation'] = self.Remote_Rotation
            setup_dict['Remote.Path'] = self.Remote_Path+os.path.sep
            setup_dict['chn_dict'] = dict([(chkey, [cid, cg, cl]) 
                                            for chkey, cid, cg, cl in 
                                            zip(setup_dict['Chn.Cmp'],
                                                setup_dict['Chn.ID'],
                                                setup_dict['Chn.Gain'],
                                                setup_dict['Chn.Length'])])
            num_comp = len(setup_dict['Chn.Cmp'])
            setup_dict['ts_info_keys'] += ['ChnGain{0}'.format(ii) 
                                           for ii in range(num_comp-1, 
                                                           num_comp+1)]
            
                                                           
    def get_survey_info(self, survey_file, station_name, rr_station_name=None):
        """
        extract information from survey file
        
        Arguments:
        ----------
            **survey_file** : string
                              full path to survey config file created by 
                              mtpy.utils.configfile
                              
            **station_name** : string
                               full station name
            
            **rr_station_name** : string
                                  full station name of remote reference
        
        """

        if survey_file is None:
            return
            
        #--> get information from survey file
        for setup_dict in self.setup_lst:
            sdict = mtcf.read_survey_configfile(survey_file)
            
            try:
                survey_dict = sdict[station_name.upper()]
                try:
                    setup_dict['chn_dict']['Hx'][0] = survey_dict['hx']
                except KeyError:
                    print 'No hx data'
                try:
                    setup_dict['chn_dict']['Hy'][0] = survey_dict['hy']
                except KeyError:
                    print 'No hy data'
                
                try:
                    if survey_dict['hz'].find('*') >= 0:
                        setup_dict['chn_dict']['Hz'][0] = '3'
                    else:
                        setup_dict['chn_dict']['Hz'][0] = survey_dict['hz']
                except KeyError:
                    print 'No hz data'
                
                try:
                    setup_dict['chn_dict']['Ex'][2] = \
                                                 survey_dict['e_xaxis_length']
                except KeyError:
                    print 'No ex data'
                try:
                    setup_dict['chn_dict']['Ey'][2] = \
                                                 survey_dict['e_yaxis_length']
                except KeyError:
                    print 'No ey data'
                    
            except KeyError:
                print ('Could not find survey information from ' 
                       '{0} for {1}'.format(survey_file, station_name))
            
            if rr_station_name is not None:
                try:
                    survey_dict = sdict[rr_station_name.upper()]
                    try:
                        setup_dict['chn_dict']['Hxr'][0] = survey_dict['hx']
                    except KeyError:
                        print 'No hxr data'
                    try:
                        setup_dict['chn_dict']['Hyr'][0] = survey_dict['hy']
                    except KeyError:
                        print 'No hyr data'
               
                except KeyError:
                    print ('Could not find survey information from ' 
                           '{0} for {1}'.format(survey_file, rr_station_name))
                           
    def write_mtft_cfg(self, cache_path, station, rrstation=None,
                       remote_path=None, survey_file=None, save_path=None):
        """
        write a config file for mtft24 from the cache files in cache_path
        
        Arguments:
        ----------
            **cache_path** : string
                             directory to cache files to be processed
            
            **station** : string
                          full name of station to be processed
            
            **rrstation** : string
                            full name of remote reference station
                            
            **remote_path** : string
                              directory to remote reference cache files
                              
            **survey_file** : string
                             full path to survey config file, written in the
                             format of mtpy.utils.configfile
                             
            **save_path** : string
                            path to save mtft24.cfg file, if none saved to
                            cache_path\mtft24.cfg
        
        """
        
        if save_path is None:
            save_path = os.path.join(cache_path, 'mtft24.cfg')

        self.cache_path = cache_path
        
        #--> get information about the time series
        self.get_ts_info_lst(cache_path)
        
        #--> get number of components
        self.compute_number_of_setups()
        
        #--> get remote reference information if needed
        if remote_path is not None:
            self.set_remote_reference_info(remote_path)
            if rrstation is None:
                rrstation = os.path.basename(os.path.dirname(
                                             os.path.dirname(remote_path)))

        self.get_rr_ts(self.ts_info_lst)
        
        #--> sort the time series such that each section with the same sampling
        #    rate is in sequential order
        self.sort_ts_lst()
        self.TS_Number = len(self.ts_info_lst)
        
        #--> fill in data from survey file
        self.get_survey_info(survey_file, station, rr_station_name=rrstation)
        
        #make a dictionary of all the values to write file
        if self.Remote_Path is not '' or self.Remote_Path is not None:
            self.Remote_Path += os.path.sep
        
        #--> set a dictionary with all attributes
        self.make_value_dict()
       
        #--> write mtft24.cfg file
        cfid = file(save_path, 'w')
        cfid.write('\n')
        #---- write processing parameters ----
        for ii, mkey in enumerate(self.meta_keys[:-1]):

            if type(self.meta_dict[mkey]) is list:
                cfid.write('${0}={1}\n'.format(mkey, ','.join(['{0}'.format(mm) 
                                             for mm in self.meta_dict[mkey]])))
            else:
                cfid.write('${0}={1}\n'.format(mkey, self.meta_dict[mkey]))
            
            #blanks line before setup and ts number
            if ii == 24:
               cfid.write('\n')
        cfid.write('\n')
        #---- write setup parameters ----
        for setup_dict in self.setup_lst:
            #set channel information                  
            setup_dict['Chn.Gain'] = [setup_dict['chn_dict'][ckey][1] 
                                      for ckey in setup_dict['Chn.Cmp']]
            setup_dict['Chn.ID'] = [setup_dict['chn_dict'][ckey][0] 
                                      for ckey in setup_dict['Chn.Cmp']]
            setup_dict['Chn.Length'] = [setup_dict['chn_dict'][ckey][2] 
                                        for ckey in setup_dict['Chn.Cmp']]
            
            for ii, mkey in enumerate(self.setup_keys):
                #write setups
                if type(setup_dict[mkey]) is list:
                    cfid.write('${0}={1}\n'.format(mkey,
                               ','.join(['{0}'.format(mm) 
                               for mm in setup_dict[mkey]])))
                else:
                    cfid.write('${0}={1}\n'.format(mkey, setup_dict[mkey]))
            cfid.write('\n')
                                    

        #---- write time series information ----
        ts_key_len = np.array([len(sd['ts_info_keys']) 
                                for sd in self.setup_lst])
        ts_key_find = np.where(ts_key_len==ts_key_len.max())[0][0]
        self.ts_info_keys = self.setup_lst[ts_key_find]['ts_info_keys']

        cfid.write(','.join(self.ts_info_keys)+'\n')
        for cfn in self.ts_info_lst:
            cfid.write(','.join([cfn[ikey] for ikey in self.ts_info_keys])+'\n')        
        
        cfid.close()
        print 'Wrote config file to {0}'.format(save_path)
        
    def read_cfg(self, cfg_fn):
        """
        read a mtft24.cfg file
        
        Arguments:
        ----------
            **cfg_fn** : full path to mtft24.cfg file to read.
        """
        
        if not os.path.isfile(cfg_fn):
            raise IOError('{0} does not exist'.format(cfg_fn))
            
        cfid = file(cfg_fn, 'r')
        clines = cfid.readlines()
        info_lst = []
        self.meta_dict = {}
        for cline in clines:
            if cline[0] == '$':
                clst = cline[1:].strip().split('=')
                self.meta_dict[clst[0]] = clst[1]
            elif cline.find('.cac') > 0:
                info_dict = {}
                clst = cline.strip().split(',')
                for ckey, cvalue in zip(self.ts_info_keys, clst):
                    info_dict[ckey] = cvalue
                info_lst.append(info_dict)
        self.ts_info_lst = info_lst
        
        cfid.close()
        
        self.set_values()
        self.make_value_dict()
        
#==============================================================================
# Deal with mtedit outputs  
#==============================================================================
class ZongeMTEdit():
    """
    deal with input and output config files for mtedit
    """
    
    def __init__(self):
        self.meta_keys = ['MTEdit:Version', 'Auto.PhaseFlip', 
                          'PhaseSlope.Smooth', 'PhaseSlope.toZMag',
                          'DPlus.Use', 'AutoSkip.onDPlus', 'AutoSkip.DPlusDev']
                          
        self.mtedit_version = '3.10d applied on {0}'.format(time.ctime())
        self.phase_flip = 'No'
        self.phaseslope_smooth = 'Minimal'
        self.phaseslope_tozmag = 'Yes'
        self.dplus_use = 'Yes'
        self.autoskip_ondplus = 'No'
        self.autoskip_dplusdev = 500.0
        
        self.meta_dict = None
        self.meta_lst = None
        
        self.cfg_fn = None
        
        self.param_header = ['Frequency  ', 'AResXYmin', 'AResXYmax', 
                              'ZPhzXYmin', 'ZPhzXYmax', 'AResYXmin', 
                              'AResYXmax', 'ZPhzYXmin', 'ZPhzYXmax', 
                              'CoherXYmin', 'CoherYXmin', 'CoherXYmax', 
                              'CoherYXmax', 'ExMin', 'ExMax', 'EyMin', 
                              'EyMax', 'HxMin', 'HxMax', 'HyMin', 'HyMax', 
                              'NFC/Stack']
                              
        self.freq_lst = [7.32420000e-04, 9.76560000e-04, 1.22070000e-03, 
                         1.46480000e-03, 1.95310000e-03, 2.44140000e-03,  
                         2.92970000e-03, 3.90620000e-03, 4.88280000e-03, 
                         5.85940000e-03, 7.81250000e-03, 9.76560000e-03, 
                         1.17190000e-02, 1.56250000e-02, 1.95310000e-02, 
                         2.34380000e-02, 3.12500000e-02, 3.90620000e-02, 
                         4.68750000e-02, 6.25000000e-02, 7.81250000e-02, 
                         9.37500000e-02, 1.25000000e-01, 1.56200000e-01, 
                         1.87500000e-01, 2.50000000e-01, 3.12500000e-01, 
                         3.75000000e-01, 5.00000000e-01, 6.25000000e-01, 
                         7.50000000e-01, 1.00000000e+00, 1.25000000e+00, 
                         1.50000000e+00, 2.00000000e+00, 2.50000000e+00, 
                         3.00000000e+00, 4.00000000e+00, 5.00000000e+00, 
                         6.00000000e+00, 8.00000000e+00, 1.00000000e+01, 
                         1.20000000e+01, 1.60000000e+01, 2.00000000e+01, 
                         2.40000000e+01, 3.20000000e+01, 4.00000000e+01, 
                         4.80000000e+01, 6.40000000e+01, 8.00000000e+01, 
                         9.60000000e+01, 1.28000000e+02, 1.60000000e+02, 
                         1.92000000e+02, 2.56000000e+02, 3.20000000e+02, 
                         3.84000000e+02, 5.12000000e+02, 6.40000000e+02, 
                         7.68000000e+02, 1.02400000e+03, 1.28000000e+03, 
                         1.53600000e+03, 2.04800000e+03, 2.56000000e+03, 
                         3.07200000e+03, 4.09600000e+03, 5.12000000e+03, 
                         6.14400000e+03, 8.19200000e+03, 1.02400000e+04, 
                         0.00000000e+00]
                         
        self.num_freq = len(self.freq_lst)
        
        #--> default parameters for MTEdit                 
        self.AResXYmin = [1.0e-2]*self.num_freq
        self.AResXYmax = [1.0e6]*self.num_freq
        self.ZPhzXYmin = [-3150.]*self.num_freq
        self.ZPhzXYmax = [3150.]*self.num_freq
        
        self.AResYXmin = [1.0e-2]*self.num_freq
        self.AResYXmax = [1.0e6]*self.num_freq
        self.ZPhzYXmin = [-3150.]*self.num_freq
        self.ZPhzYXmax = [3150.]*self.num_freq
        
        self.CoherXYmin = [0.6]*self.num_freq
        self.CoherYXmin = [0.6]*self.num_freq
        self.CoherXYmax = [0.999]*self.num_freq
        self.CoherYXmax = [0.999]*self.num_freq
        
        self.ExMin = [0]*self.num_freq
        self.ExMax = [1.0e6]*self.num_freq
        
        self.EyMin = [0]*self.num_freq
        self.EyMax = [1.0e6]*self.num_freq
        
        self.HxMin = [0]*self.num_freq
        self.HxMax = [1.0e6]*self.num_freq
        
        self.HyMin = [0]*self.num_freq
        self.HyMax = [1.0e6]*self.num_freq
        
        self.NFCStack = [8]*self.num_freq
        
        self.param_dict = None
        self.param_lst = None
        
        self.string_fmt_lst = ['.4e', '.4e', '.4e', '.1f', '.1f', '.4e', '.4e',
                               '.1f', '.1f', '.3f', '.3f', '.3f', '.3f', '.1g',
                               '.4e', '.1g', '.4e', '.1g', '.4e', '.1g', '.4e',
                               '.0f']
        
    def make_meta_dict(self):
        """
        make meta data dictionary
        """
        if not self.meta_lst:
            self.make_meta_lst()
            
        self.meta_dict = dict([(mkey, mvalue) for mkey, mvalue in 
                                zip(self.meta_keys, self.meta_lst)])
                                
    def make_meta_lst(self):
        """
        make metadata list
        """
        
        self.meta_lst = [self.mtedit_version,
                         self.phase_flip,
                         self.phaseslope_smooth,
                         self.phaseslope_tozmag,
                         self.dplus_use,
                         self.autoskip_ondplus,
                         self.autoskip_dplusdev]
        
    def make_param_dict(self):
        """
        make a parameter dictionary
        """
        if not self.param_lst:
            self.make_param_lst()
            
        self.param_dict = dict([(mkey, mvalue) for mkey, mvalue in
                                 zip(self.param_header, self.param_lst)])
        
    def make_param_lst(self):
        """
        make a list of parameters
        """
        
        self.param_lst = [self.freq_lst,
                          self.AResXYmin, 
                          self.AResXYmax, 
                          self.ZPhzXYmin, 
                          self.ZPhzXYmax,
                          self.AResYXmin, 
                          self.AResYXmax, 
                          self.ZPhzYXmin, 
                          self.ZPhzYXmax,
                          self.CoherXYmin,
                          self.CoherYXmin,
                          self.CoherXYmax,
                          self.CoherYXmax,
                          self.ExMin,
                          self.ExMax,
                          self.EyMin,
                          self.EyMax,
                          self.HxMin,
                          self.HxMax,
                          self.HyMin,
                          self.HyMax,
                          self.NFCStack]
                          

    def read_config(self, cfg_fn):
        """
        read a MTEdit.cfg file
        """

        if not os.path.isfile(cfg_fn):
            raise IOError('{0} does not exist'.format(cfg_fn))
            
        self.cfg_fn = cfg_fn
        self.meta_dict = {}
        self.param_dict = {}
        
        cfid = file(cfg_fn, 'r')
        clines = cfid.readlines()
        for ii, cline in enumerate(clines):
            #--> get metadata 
            if cline[0] == '$':
                clst = cline[1:].strip().split('=')
                self.meta_dict[clst[0]] = clst[1]
            
            #--> get filter parameters header            
            elif cline.find('Frequency') == 0:
                pkeys = [cc.strip() for cc in cline.strip().split(',')]
                nparams = len(clines)-ii
                self.param_dict = dict([(pkey, np.zeros(nparams))
                                           for pkey in pkeys])
                jj = 0
            
            #--> get filter parameters as a function of frequency
            else:
                if len(cline) > 3:
                    clst = [cc.strip() for cc in cline.strip().split(',')]
                    for nn, pkey in enumerate(pkeys):
                        self.param_dict[pkey][jj] = float(clst[nn])
                    jj += 1
        self.num_freq = len(self.param_dict['Frequency'])
                    
    def write_config(self, save_path, mtedit_params_dict=None):
        """
        write a mtedit.cfg file        
        
        """

        if os.path.isdir(save_path) == True:
            save_path = os.path.join(save_path, 'mtedit.cfg')
        
        self.cfg_fn = save_path
        if not self.meta_dict:
            self.make_meta_dict()
            
        if not self.param_dict:
            self.make_param_dict()
        
        #--- write file ---
        cfid = file(self.cfg_fn, 'w')
        
        #--> write metadata
        for mkey in self.meta_keys:
            cfid.write('${0}={1}\n'.format(mkey, self.meta_dict[mkey]))
        
        #--> write parameter header
        for header in self.param_header[:-1]:
            cfid.write('{0:>11},'.format(header))
        cfid.write('{0:>11}\n'.format(self.param_header[-1]))
        
        #--> write filter parameters
        for ii in range(self.num_freq):
            for jj, pkey in enumerate(self.param_header[:-1]):
                cfid.write('{0:>11},'.format('{0:{1}}'.format(
                                self.param_dict[pkey][ii], 
                                self.string_fmt_lst[jj])))
            cfid.write('{0:>11}\n'.format('{0:{1}}'.format(
                                self.param_dict[self.param_header[-1]][ii], 
                                self.string_fmt_lst[-1])))
    
        cfid.close()
        print 'Wrote mtedit config file to {0}'.format(self.cfg_fn)
        
    
#==============================================================================
# deal with avg files output from mtedit
#==============================================================================    
class ZongeMTAvg():
    """
    deal with avg files output from mtedit
    
    """                     

    def __init__(self):
        
        
        self.Survey_Type = 'NSAMT'
        self.Survey_Array = 'Tensor'
        self.Tx_Type = 'Natural'
        self.MTEdit3Version = '3.001 applied on 2010-11-19'
        self.MTEdit3Auto_PhaseFlip = 'No'
        self.MTEdit3PhaseSlope_Smooth = 'Moderate'
        self.MTEdit3PhaseSlope_toMag = 'No'
        self.MTEdit3DPlus_Use = 'No'
        self.Rx_GdpStn = 4
        self.Rx_Length = 100
        self.Rx_HPR = [90, 0, 0]
        self.Unit_Length = 'm'
        self.header_dict = {'Survey.Type':self.Survey_Type,
                            'Survey.Array':self.Survey_Array,
                            'Tx.Type':self.Tx_Type,
                            'MTEdit:Version':self.MTEdit3Version,
                            'MTEdit:Auto.PhaseFlip':self.MTEdit3Auto_PhaseFlip,
                            'MTEdit:PhaseSlope.Smooth':self.MTEdit3PhaseSlope_Smooth,
                            'MTEdit:PhaseSlope.toZmag':self.MTEdit3PhaseSlope_toMag,
                            'MTEdit:DPlus.Use':self.MTEdit3DPlus_Use,
                            'Rx.GdpStn':self.Rx_GdpStn,
                            'Rx.Length':self.Rx_Length,
                            'Rx.HPR':self.Rx_HPR,
                            'Unit.Length':self.Unit_Length}
        self.info_keys = ['Skp', 'Freq', 'E.mag', 'B.mag', 'Z.mag', 'Z.phz',
                          'ARes.mag', 'ARes.%err', 'Z.perr', 'Coher', 
                          'FC.NUse', 'FC.NTry']
        self.info_type = [np.int, np.float, np.float, np.float, np.float, 
                          np.float, np.float, np.float, np.float, np.float, 
                          np.int, np.int]
        self.info_dtype = np.dtype([(kk.lower(), tt) 
                                    for kk, tt in zip(self.info_keys, 
                                                      self.info_type)])
                          
        self.Z = mtz.Z()
        self.Tipper = mtz.Tipper()
        self.comp_lst_z = ['zxx','zxy','zyx','zyy']
        self.comp_lst_tip = ['tzx','tzy']
        self.comp_index = {'zxx':(0,0), 'zxy':(0,1), 'zyx':(1,0), 'zyy':(1,1),
                           'tzx':(0,0), 'tzy':(0,1)}
        self.comp_flag = {'zxx':False, 'zxy':False, 'zyx':False, 'zyy':False,
                          'tzx':False, 'tzy':False}
        self.comp_dict = None
        self.comp = None
        self.nfreq = None
        self.nfreq_tipper = None
        self.freq_dict = None
        self.avg_dict = {'ex':'4', 'ey':'5'}

        
    def read_avg_file(self, avg_fn):
        """
        read in average file        
        """
        
        if not os.path.isfile(avg_fn):
            raise IOError('{0} does not exist, check file'.format(avg_fn))
        
        self.comp = os.path.basename(avg_fn)[0]
        afid = file(avg_fn)
        alines = afid.readlines()
        self.comp_flag = {'zxx':False, 'zxy':False, 'zyx':False, 'zyy':False,
                          'tzx':False, 'tzy':False}
                          
        self.comp_dict = dict([(ckey, np.zeros(len(alines)/4, 
                                               dtype=self.info_dtype))
                                for ckey in self.comp_flag.keys()])
        self.comp_lst_z = []
        self.comp_lst_tip = []
        ii = 0                        
        for aline in alines:
            if aline.find('=') > 0 and aline.find('$') == 0:
                alst = [aa.strip() for aa in aline.strip().split('=')]
                if alst[1].lower() in self.comp_flag.keys():
                    akey = alst[1].lower()
                    self.comp_flag[akey] = True
                    if akey[0] == 'z':
                        self.comp_lst_z.append(akey)
                    elif akey[0] == 't':
                        self.comp_lst_tip.append(akey)
                    ii = 0
                else:
                    self.header_dict[alst[0][1:]] = alst[1]
            elif aline[0] == 'S':
                pass
            elif len(aline) > 2:
                alst = [aa.strip() for aa in aline.strip().split(',')]
                for cc, ckey in enumerate(self.info_keys):
                    self.comp_dict[akey][ii][ckey.lower()] = alst[cc]
                ii += 1
     
        self.fill_Z()
        self.fill_Tipper()
        
        print 'Read file {0}'.format(avg_fn)
        
    def convert2complex(self, zmag, zphase):
        """
        outputs of mtedit are magnitude and phase of z, convert to real and
        imaginary parts, phase is in milliradians
        
        """
        if type(zmag) is np.ndarray:
            assert len(zmag) == len(zphase)
        
        
        zreal = zmag*np.cos(zphase/1000%np.pi)
        zimag = zmag*np.sin(zphase/1000%np.pi)
        
        return zreal, zimag
        
    def fill_Z(self):
        """
        create Z array with data
        """
        flst = np.array([len(np.nonzero(self.comp_dict[comp]['freq'])[0])
                         for comp in self.comp_lst_z])
        
        nz = flst.max()
        freq = self.comp_dict[self.comp_lst_z[np.where(flst==nz)[0][0]]]['freq']
        freq = freq[np.nonzero(freq)]

        if self.nfreq:
            if nz > self.nfreq:
                self.freq_dict = dict([('{0:.4g}'.format(ff), nn) for nn, ff
                                       in enumerate(freq)])
                self.nfreq = nz
                #reshape z
                new_Z = mtz.Z()
                new_Z.z = np.zeros((nz, 2, 2), dtype='complex')
                new_Z.zerr = np.zeros((nz, 2, 2))
                nzx, nzy, nzz = self.Z.z.shape
                new_Z.z[0:nzx, 0:nzy, 0:nzz] = self.Z.z
                new_Z.zerr[0:nzx, 0:nzy, 0:nzz] = self.Z.zerr
                new_Z.freq = freq
                self.Z = new_Z
            
            #fill z with values from comp_dict
            for ikey in self.comp_lst_z:
                ii, jj = self.comp_index[ikey]

                zr, zi = self.convert2complex(self.comp_dict[ikey]['z.mag'][:nz],
                                              self.comp_dict[ikey]['z.phz'][:nz])
                if nz != self.nfreq:
                    for kk, zzr, zzi in zip(range(len(zr)), zr, zi):
                        ll = self.freq_dict['{0:.4g}'.format(
                                            self.comp_dict[ikey]['freq'][kk])]
                        if ikey.find('yx') > 0:
                            self.Z.z[ll, ii, jj] = -1*(zzr+zzi*1j)
                        else:
                            self.Z.z[ll, ii, jj] = zzr+zzi*1j
                        self.Z.zerr[ll,ii, jj] = \
                                    self.comp_dict[ikey]['ares.%err'][kk]*.005
                else:
                    if ikey.find('yx') > 0:
                         self.Z.z[:, ii, jj] = -1*(zr+zi*1j)
                    else:
                        self.Z.z[:, ii, jj] = zr+zi*1j

                    self.Z.zerr[:,ii, jj] = \
                                     self.comp_dict[ikey]['ares.%err'][:nz]*.005
           
        else:
            self.nfreq = nz
            self.freq_dict = dict([('{0:.4g}'.format(ff), nn) for nn, ff
                                       in enumerate(freq)])
            #fill z with values
            z = np.zeros((nz, 2, 2), dtype='complex')
            zerr = np.zeros((nz, 2, 2))
            
            for ikey in self.comp_lst_z:
                ii, jj = self.comp_index[ikey]
                    
                zr, zi = self.convert2complex(self.comp_dict[ikey]['z.mag'][:nz],
                                              self.comp_dict[ikey]['z.phz'][:nz])
                
                if ikey.find('yx') > 0:
                    z[:, ii, jj] = -1*(zr+zi*1j)
                else:
                    z[:, ii, jj] = zr+zi*1j

                zerr[:,ii, jj] = self.comp_dict[ikey]['ares.%err'][:nz]*.005 
                    
            self.Z.z = z
            self.Z.zerr = zerr
            self.Z.freq = freq
            
        self.Z.z = np.nan_to_num(self.Z.z)
        self.Z.zerr = np.nan_to_num(self.Z.zerr)
                
                
    def fill_Tipper(self):
        """
        fill tipper values
        """
        
        flst = np.array([len(np.nonzero(self.comp_dict[comp]['freq'])[0])
                         for comp in self.comp_lst_tip])
        nz = flst.max()
        freq = self.comp_dict[self.comp_lst_tip[np.where(flst==nz)[0][0]]]['freq']
        freq = freq[np.nonzero(freq)]
        if self.nfreq_tipper and self.Tipper.tipper is not None:
            if nz > self.nfreq_tipper:
                self.freq_dict = dict([('{0:.4g}'.format(ff), nn) for nn, ff
                                       in enumerate(freq)])
                self.nfreq_tipper = nz
                #reshape tipper
                new_Tipper = mtz.Tipper()
                new_Tipper.tipper = np.zeros((nz, 1, 2), dtype='complex')
                new_Tipper.tipper_err = np.zeros((nz, 1, 2))
                nzx, nzy, nzz = self.Tipper.tipper.shape
                new_Tipper.tipper[0:nzx, :, 0:nzz] = self.Tipper.tipper
                new_Tipper.tipper_err[0:nzx, :, 0:nzz] = self.Tipper.tipper_err
                new_Tipper.freq = freq
                self.Tipper = new_Tipper
           
            #fill z with values from comp_dict
            for ikey in self.comp_lst_tip:
                ii, jj = self.comp_index[ikey]

                tr, ti = self.convert2complex(self.comp_dict[ikey]['z.mag'][:nz],
                                              self.comp_dict[ikey]['z.phz'][:nz])
                if nz != self.nfreq_tipper:
                    for kk, tzr, tzi in zip(range(len(tr)), tr, ti):
                        ll = self.freq_dict['{0:.4g}'.format(
                                            self.comp_dict[ikey]['freq'][kk])]
                        self.Tipper.tipper[ll, ii, jj] += tzr+tzi*1j
                        self.Tipper.tipper_err[ll,ii, jj] += \
                                    self.comp_dict[ikey]['ares.%err'][kk]*\
                                                    .05*np.sqrt(tzr**2+tzi**2)
                else:
                    self.Tipper.tipper[:, ii, jj] += tr+ti*1j
                    self.Tipper.tipper_err[:, ii, jj] += \
                                     self.comp_dict[ikey]['ares.%err'][:nz]*\
                                                     .05*np.sqrt(tr**2+ti**2)
            
            #apparently need to average the outputs from the two .avg files                                         
            self.Tipper.tipper /= 2.
            self.Tipper.tipper_err / 2.
           
        else:
            self.nfreq_tipper = nz
            self.freq_dict = dict([('{0:.4g}'.format(ff), nn) for nn, ff
                                       in enumerate(freq)])
            #fill z with values
            tipper = np.zeros((nz, 1, 2), dtype='complex')
            tippererr = np.zeros((nz, 1, 2))
            
            for ikey in self.comp_lst_tip:
                ii, jj = self.comp_index[ikey]
                    
                tr, ti = self.convert2complex(self.comp_dict[ikey]['z.mag'][:nz],
                                              self.comp_dict[ikey]['z.phz'][:nz])
                
                tipper[:, ii, jj].real = tr
                tipper[:, ii, jj].imag = ti
                tippererr[:,ii, jj] = self.comp_dict[ikey]['ares.%err'][:nz]*\
                                                     .05*np.sqrt(tr**2+ti**2)
                    
            self.Tipper.tipper = tipper
            self.Tipper.tipper_err = tippererr
            self.Tipper.freq = freq
            
        self.Tipper.tipper = np.nan_to_num(self.Tipper.tipper)
        self.Tipper.tipper_err = np.nan_to_num(self.Tipper.tipper_err)
        
    def write_edi(self, avg_dirpath, station, survey_dict=None, 
                  survey_cfg_file=None,  mtft_cfg_file=None, 
                  mtedit_cfg_file=r"c:\MinGW32-xy\Peacock\zen\bin\mtedit.cfg", 
                  save_path=None, rrstation=None, 
                  copy_path=r"d:\Peacock\MTData\EDI_Files", avg_ext='.avg'):
        """
        write an edi file from the .avg files
        
        Arguments:
        ----------
            **fnx** : string (full path to electric north file)
                      file for Zxx, Zxy
                      
            **fny** : string (full path to electric east file)
                      file for Zyx, Zyy
            
            **survey_dict** : dictionary
                              dictionary containing the survey parameters
                              such as lat, lon, elevation, date, etc.
                              
            **survey_cfg_file** : string (full path to survey file)
                              file contains all the important information 
                              about the setup of the station, input file if
                              survey_dict is None.  This is created by 
                              mtpy.configfile
                              
            **mtft_cfg_file** : string (full path to mtft24.cfg file)
                               this file contains information on how the
                               Fourier coefficients were calculated
                               
            **mtedit_cfg_file** : string (full path to MTEdit.cfg file)
                                  this file contains information on how 
                                  the transfer functions were estimated
            
            **save_path** : string (full path or directory to where .edi file 
                                    will be saved)
                                    
        Outputs:
        ---------
            **edi_fn** : string (full path to .edi file)
                      
                      
                      
        """
        
        if save_path is None:
            save_dir = os.path.dirname(avg_dirpath)
            save_path = os.path.join(save_dir, station+'.edi')
        print save_path
        
        #create an mtedi instance
        self.edi = mtedi.Edi()
        self.edi.Z = self.Z
        self.edi.Tipper = self.Tipper
        
        
        #read in ex file
        fnx = os.path.join(avg_dirpath, 
                           self.avg_dict['ex'],
                           self.avg_dict['ex']+avg_ext)
        if os.path.isfile(fnx) == True:
            self.read_avg_file(fnx)
        
        #read in ey file
        fny = os.path.join(avg_dirpath, 
                           self.avg_dict['ey'],
                           self.avg_dict['ey']+avg_ext)
        if os.path.isfile(fny) == True:
            self.read_avg_file(fny)
 
        
        #read in survey file
        if survey_cfg_file is not None:
            sdict = mtcf.read_survey_configfile(survey_cfg_file)
            
        try:
            survey_dict = sdict[station.upper()]
        except KeyError:
            try:
                survey_dict['station']
            except KeyError:
                try:
                    survey_dict['station_name']
                except KeyError:
                    raise KeyError('Could not find station information in'
                                   ', check inputs')
                                 
        #get remote reference information if desired
        if rrstation:
            try:
                rrsurvey_dict = sdict[rrstation.upper()]
            except KeyError:
                print 'Could not find station information for remote reference'
        else:
            rrsurvey_dict = None
            
        #read in mtft24.cfg file
        if mtft_cfg_file is None:
            try:
                mtft_cfg_file = os.path.join(avg_dirpath, 'mtft24.cfg')
                zmtft = ZongeMTFT()
                zmtft.read_cfg(mtft_cfg_file)
                mtft_dict = zmtft.meta_dict
            except:
                mtft_dict = None
        else:
            zmtft = ZongeMTFT()
            zmtft.read_cfg(mtft_cfg_file)
            mtft_dict = zmtft.meta_dict
            
        #read in mtedit.cfg file
        if mtedit_cfg_file:
            zmtedit = ZongeMTEdit()
            zmtedit.read_config(mtedit_cfg_file)
            mtedit_dict = zmtedit.meta_dict
        else:
            mtedit_dict = None
            
        #----------------HEAD BLOCK------------------
        #from survey dict get information
        head_dict = {}

        #--> data id
        try:
            head_dict['dataid'] = survey_dict['station']
        except KeyError:
            head_dict['dataid'] = station
            
        #--> acquired by
        head_dict['acqby'] = survey_dict.pop('network','')
        
        #--> file by
        head_dict['fileby'] = survey_dict.pop('network','')
        
        #--> acquired date
        head_dict['acqdate'] = survey_dict.pop('date', '')
        
        #--> file date
        head_dict['acqdate'] = time.strftime('%Y-%m-%d',time.localtime())
        
        #--> prospect
        head_dict['loc'] = survey_dict.pop('location', '')
        
        #--> latitude
        head_dict['lat'] = MTft._assert_position_format('lat',
                                                   survey_dict.pop('lat',0.0))
        
        #--> longitude
        head_dict['lon'] = MTft._assert_position_format('lon',
                                                   survey_dict.pop('lon',0.0))
        
        #--> elevation
        head_dict['elev'] = survey_dict.pop('elevation', 0)
        
        #--> set header dict as attribute of edi
        self.edi.head = head_dict
       
       #-----------------INFO BLOCK---------------------------
        info_dict = {}
        info_dict['max lines'] = 1000
        
        #--> put the rest of the survey parameters in the info block
        info_dict['Survey Paramters'] = ''
        for skey in survey_dict.keys():
            info_dict[skey] = survey_dict[skey]
        
        #--> put parameters about how fourier coefficients were found
        if mtft_dict:
            info_dict['mtft24 parameters'] = ''
            for mkey in mtft_dict.keys():
                info_dict[mkey] = mtft_dict[mkey]
        
        #--> put parameters about how transfer function was found
        if mtedit_dict:
            info_dict['mtedit parameters'] = ''
            for mkey in mtedit_dict.keys():
                info_dict[mkey] = mtedit_dict[mkey]
        
        #--> set info dict as attribute of edi
        self.edi.info_dict = info_dict
                
        #----------------DEFINE MEASUREMENT BLOCK------------------
        definemeas_dict = {}
        
        definemeas_dict['maxchan'] = 5
        definemeas_dict['maxrun'] = 999
        definemeas_dict['maxmeas'] = 99999
        try:
            definemeas_dict['units'] = mtedit_dict['unit.length']
        except (TypeError, KeyError):
            definemeas_dict['units'] = 'm'
        definemeas_dict['reftypy'] = 'cartesian'
        if rrsurvey_dict: 
            definemeas_dict['reflat'] = MTft._assert_position_format('lat',
                                rrsurvey_dict.pop('lat',0.0))
            definemeas_dict['reflon'] = MTft._assert_position_format('lon',
                                rrsurvey_dict.pop('lon', 0.0))
            definemeas_dict['refelev'] = rrsurvey_dict.pop('elev',0.0)
        else:
            definemeas_dict['reflat'] = head_dict['lat']
            definemeas_dict['reflon'] = head_dict['lon']
            definemeas_dict['refelev'] = head_dict['elev']
        
        #--> set definemeas as attribure of edi
        self.edi.definemeas = definemeas_dict
        
        #------------------HMEAS_EMEAS BLOCK--------------------------
        hemeas_lst = []
        if mtft_dict:
            chn_lst = mtft_dict['Chn.Cmp']
            chn_id = mtft_dict['Chn.ID']
            chn_len_lst = mtft_dict['Chn.Length']
        else:
            chn_lst = ['hx', 'hy', 'hz', 'ex', 'ey']
            chn_id = [1, 2, 3, 4, 5]
            chn_len_lst = [100]*5
        
        #--> hx component                
        try:
            hxazm = survey_dict['b_xaxis_azimuth']
        except KeyError:
            hxazm = 0
        hemeas_lst.append(['HMEAS', 
                           'ID={0}'.format(chn_id[0]), 
                           'CHTYPE={0}'.format(chn_lst[0].upper()), 
                           'X=0', 
                           'Y=0', 
                           'AZM={0}'.format(hxazm),
                           ''])
        #--> hy component
        try:
            hyazm = survey_dict['b_yaxis_azimuth']
        except KeyError:
            hyazm = 90
        hemeas_lst.append(['HMEAS', 
                           'ID={0}'.format(chn_id[1]), 
                           'CHTYPE={0}'.format(chn_lst[1].upper()), 
                           'X=0', 
                           'Y=0', 
                           'AZM={0}'.format(hyazm),
                           ''])

        #--> hz component
        hemeas_lst.append(['HMEAS', 
                           'ID={0}'.format(chn_id[2]), 
                           'CHTYPE={0}'.format(chn_lst[2].upper()), 
                           'X=0', 
                           'Y=0', 
                           'AZM={0}'.format(0),
                           ''])
        #--> ex component
        hemeas_lst.append(['EMEAS', 
                           'ID={0}'.format(chn_id[3]), 
                           'CHTYPE={0}'.format(chn_lst[3].upper()), 
                           'X=0', 
                           'Y=0', 
                           'X2={0}'.format(chn_len_lst[3]),
                           'Y2=0'])
                           
        #--> ey component
        hemeas_lst.append(['EMEAS', 
                           'ID={0}'.format(chn_id[4]), 
                           'CHTYPE={0}'.format(chn_lst[4].upper()), 
                           'X=0', 
                           'Y=0', 
                           'X2=0',
                           'Y2={0}'.format(chn_len_lst[4])])
                           
        #--> remote reference 
        if rrsurvey_dict:
            hxid = rrsurvey_dict.pop('hx', 6)
            hyid = rrsurvey_dict.pop('hy', 7)
            hxazm = rrsurvey_dict.pop('b_xaxis_azimuth', 0)
            hyazm = rrsurvey_dict.pop('b_xaxis_azimuth', 90)
        else:
            hxid =  6
            hyid =  7
            hxazm = 0
            hyazm = 90
                
        #--> rhx component
        hemeas_lst.append(['HMEAS', 
                           'ID={0}'.format(hxid), 
                           'CHTYPE={0}'.format('rhx'.upper()), 
                           'X=0', 
                           'Y=0', 
                           'AZM={0}'.format(hxazm),
                           ''])
        #--> rhy component
        hemeas_lst.append(['HMEAS', 
                           'ID={0}'.format(hyid), 
                           'CHTYPE={0}'.format('rhy'.upper()), 
                           'X=0', 
                           'Y=0', 
                           'AZM={0}'.format(hyazm),
                           ''])
        hmstring_lst = []
        for hm in hemeas_lst:
            hmstring_lst.append(' '.join(hm))
        #--> set hemeas as attribute of edi
        self.edi.hmeas_emeas = hmstring_lst
        
        #----------------------MTSECT-----------------------------------------
        mtsect_dict = {}
        mtsect_dict['sectid'] = station
        mtsect_dict['nfreq'] = len(self.Z.freq)
        for chn, chnid in zip(chn_lst, chn_id):
            mtsect_dict[chn] = chnid
        
        #--> set mtsect as attribure of edi
        self.edi.mtsect = mtsect_dict
        
        #----------------------ZROT BLOCK--------------------------------------
        self.edi.zrot = np.zeros(len(self.edi.Z.z))
        
        #----------------------FREQUENCY BLOCK---------------------------------
        self.edi.freq = self.Z.freq
        
            
        #============ WRITE EDI FILE ==========================================
        edi_fn = self.edi.writefile(save_path)
        
        print 'Wrote .edi file to {0}'.format(edi_fn)
        
        if copy_path is not None:
            copy_edi_fn = os.path.join(copy_path, os.path.basename(edi_fn))
            if not os.path.exists(copy_path):
                os.mkdir(copy_path)
            shutil.copy(edi_fn, copy_edi_fn)
            print 'Copied {0} to {1}'.format(edi_fn, copy_edi_fn)
        
        return edi_fn
        
        
        
            
            
        
        
            
            
        
        
        
        

        
                    
        
        
        
        
        
        
        
    

    
    
    

    
    