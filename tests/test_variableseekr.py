#!/usr/bin/env python

import nose
import logging
l = logging.getLogger("angr.tests")

try:
    # pylint: disable=W0611,F0401
    import standard_logging
    import angr_debug
except ImportError:
    pass

import angr, simuvex

# load the tests
import os
test_location = str(os.path.dirname(os.path.realpath(__file__)))
projects = {}
projects['fauxwares'] = {}
projects['cfg_1'] = {}
projects['allcmps'] = {}
projects['basic_buffer_overflows'] = {}

def setup_x86():
    fauxware = projects['fauxwares']
    fauxware['x86'] = angr.Project(test_location + "/blob/i386/fauxware",  arch="X86")

def setup_amd64():
    fauxware = projects['fauxwares']
    cfg_1 = projects['cfg_1']
    all_cmps = projects['allcmps']
    basic_buffer_overflows = projects['basic_buffer_overflows']

    fauxware['amd64'] = angr.Project(test_location + "/blob/x86_64/fauxware",  arch="AMD64")
    cfg_1['amd64'] = angr.Project(test_location + "/blob/x86_64/cfg_1", arch="AMD64")
    all_cmps['amd64'] = angr.Project(test_location + '/blob/x86_64/allcmps', arch="AMD64")
    basic_buffer_overflows['amd64'] = angr.Project(test_location + '/blob/x86_64/basic_buffer_overflows')

def setup_ppc32():
    fauxware = projects['fauxwares']
    fauxware['ppc32'] = angr.Project(test_location + "/blob/ppc/fauxware",  arch="PPC32")

def setup_mipsel():
    fauxware = projects['fauxwares']
    fauxware['mipsel'] = angr.Project(test_location + "/blob/mipsel/fauxware",  arch=simuvex.SimMIPS32(endness="Iend_LE"))

def setup_arm():
    fauxware = projects['fauxwares']
    fauxware['arm'] = angr.Project(test_location + "/blob/armel/fauxware",  arch=simuvex.SimARM(endness="Iend_LE"))

def setup_module():
    setup_x86()
    setup_amd64()
    setup_arm()
    setup_ppc32()
    setup_mipsel()

def test_fauxware(arch, start):
    fauxware = projects['fauxwares']
    cfg = fauxware[arch].construct_cfg()
    vfg = fauxware[arch].construct_vfg(start=start)
    variable_seekr = angr.VariableSeekr(fauxware[arch], cfg, vfg)
    variable_seekr.construct(func_start=start)
    function_manager = cfg.function_manager
    for func_addr, func in function_manager.functions.items():
        l.info("Function %08xh", func_addr)
        variable_manager = variable_seekr.get_variable_manager(func_addr)
        if variable_manager is None:
            continue
        # TODO: Check the result returned
        l.info("Variables: ")
        for var in variable_manager.variables:
            if isinstance(var, angr.StackVariable):
                l.info(var.detail_str())
            else:
                l.info("%s(%d),  referenced at %08x", var, var._size, var._inst_addr)

def test_cfg_1(arch, start):
    cfg_1 = projects['cfg_1']
    cfg = cfg_1[arch].construct_cfg()
    vfg = cfg_1[arch].construct_vfg(start=start)
    variable_seekr = angr.VariableSeekr(cfg_1[arch], cfg, vfg)
    variable_seekr.construct(func_start=start)
    function_manager = cfg.function_manager
    for func_addr, func in function_manager.functions.items():
        l.info("Function %08xh", func_addr)
        variable_manager = variable_seekr.get_variable_manager(func_addr)
        if variable_manager is None:
            continue
        # TODO: Check the result returned
        l.info("Variables: ")
        for var in variable_manager.variables:
            if isinstance(var, angr.StackVariable):
                l.info(var.detail_str())
            else:
                l.info("%s(%d),  referenced at %08x", var, var._size, var._inst_addr)

def test_allcmps(arch, starts):
    allcmps = projects['allcmps']
    cfg = allcmps[arch].construct_cfg()
    for start in starts:
        allcmps[arch].construct_vfg(start=start)
    vfg = allcmps[arch].vfg
    variable_seekr = angr.VariableSeekr(allcmps[arch], cfg, vfg)

    for start in starts:
        variable_seekr.construct(func_start=start)
        function_manager = cfg.function_manager
        for func_addr, func in function_manager.functions.items():
            l.info("Function %xh", func_addr)
            variable_manager = variable_seekr.get_variable_manager(func_addr)
            if variable_manager is None:
                continue
            # TODO: Check the result returned
            l.info("Variables: ")
            for var in variable_manager.variables:
                if isinstance(var, angr.StackVariable):
                    l.info(var.detail_str())
                else:
                    l.info("%s(%d),  referenced at %08x", var, var._size, var._inst_addr)

def test_basic_buffer_overflows(arch, starts):
    basic_buffer_overflows = projects['basic_buffer_overflows']
    cfg = basic_buffer_overflows[arch].construct_cfg()
    for start in starts:
        basic_buffer_overflows[arch].construct_vfg(start=start)
    vfg = basic_buffer_overflows[arch].vfg
    variable_seekr = angr.VariableSeekr(basic_buffer_overflows[arch], cfg, vfg)

    for start in starts:
        variable_seekr.construct(func_start=start)
        function_manager = cfg.function_manager
        for func_addr, func in function_manager.functions.items():
            l.info("Function %xh", func_addr)
            variable_manager = variable_seekr.get_variable_manager(func_addr)
            if variable_manager is None:
                continue
            # TODO: Check the result returned
            l.info("Variables: ")
            for var in variable_manager.variables:
                if isinstance(var, angr.StackVariable):
                    l.info(var.detail_str())
                else:
                    l.info("%s(%d),  referenced at %08x", var, var._size, var._inst_addr)


if __name__ == "__main__":
    logging.getLogger('angr.cfg').setLevel(logging.DEBUG)
    logging.getLogger('angr.vfg').setLevel(logging.DEBUG)
    logging.getLogger('simuvex.plugins.symbolic_memory').setLevel(logging.INFO)
    logging.getLogger('claripy.claripy').setLevel(logging.ERROR)
    l.setLevel(logging.DEBUG)
    setup_amd64()
    l.info("LOADED")
    #test_fauxware('amd64', 0x40071d)
    test_basic_buffer_overflows('amd64', (0x40068f, 0x40055c, 0x4005b6, 0x40063e))
    l.info("DONE")