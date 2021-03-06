import os
import sys
# these paths allow for importing modules from the actors package both in the
# docker container and native when the test suite is launched from the CLI
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
sys.path.insert(0, PARENT)
sys.path.append('/tacconfig')
import pytest
from tacconfig import config


def test_load_yml():
    '''test load valid YML by path as a dict'''
    testdata = os.path.join(HERE, 'data', '1')
    fname = 'config.yml'
    settings = config.read_config(places_list=[testdata],
                                  config_filename=fname,
                                  permissive=False)
    assert isinstance(settings, dict), "Expected to get a 'dict' back"
    assert 'filter' in settings, "Expected 'filter' in response"


def test_invalid_yml():
    '''robust to invalid YML by path as a dict'''
    testdata = os.path.join(HERE, 'data', '1')
    fname = 'invalid.yml'
    settings = config.read_config(places_list=[testdata],
                                  config_filename=fname,
                                  permissive=True)
    assert settings == {}


def test_invalid_filetype():
    '''test that filetype is among the ones accepted'''
    testdata = os.path.join(HERE, 'data', '1')
    fname = 'config.yml'
    with pytest.raises(AssertionError):
        config.read_config(places_list=[testdata],
                           config_filename=fname,
                           permissive=False,
                           filetype="JSON")


def test_specified_load_order():
    '''test that config later in list takes precedence'''
    testdata = []
    testdata.append(os.path.join(HERE, 'data', '1'))
    testdata.append(os.path.join(HERE, 'data', '2'))
    fname = 'config.yml'
    settings = config.read_config(places_list=testdata,
                                  config_filename=fname,
                                  permissive=True)
    assert settings['logs']['level'] == 'INFO', \
        "Expected setting from second location to apply"
    assert isinstance(settings['tacos'], list), \
        "Expected setting to contain a list named 'tacos'"


def test_environment_override():
    '''ensure environment override works as intended'''
    testdata = []
    testdata.append(os.path.join(HERE, 'data', '1'))
    testdata.append(os.path.join(HERE, 'data', '2'))
    fname = 'config.yml'
    namespace = 'TACCONFIG'
    env_var_name = config.variablize(keys=['logs', 'level'],
                                     namespace=namespace)
    os.environ[env_var_name] = 'WARNING'
    # override logs.level with WARNING
    settings = config.read_config(places_list=testdata,
                                  config_filename=fname,
                                  namespace=namespace,
                                  permissive=True,
                                  env=True)
    assert settings['logs']['level'] == 'WARNING', 'Override failed'
    # turn off override by setting env to False
    settings = config.read_config(places_list=testdata,
                                  config_filename=fname,
                                  namespace=namespace,
                                  permissive=True,
                                  env=False)
    assert settings['logs']['level'] == 'INFO', 'Ignore env failed'


def test_get_env_config_vals():
    '''ensure we can get a list of candidate redact values from env'''
    os.environ['TEST_SECTION1'] = "abc"
    os.environ['TEST_SECTION2_KEY1'] = "123"
    os.environ['NOT_SECTION2_KEY1'] = "def"
    env_vals = config.get_env_config_vals(namespace='TEST')
    assert set(env_vals) == set(['abc', '123'])
