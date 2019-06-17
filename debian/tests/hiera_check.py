import sys
import hiera

HIERA_CONFIG_FILE = './hiera.yaml'
EXITCODE='0'

def print_test_info(key_name, env, exp_value_data):
    print('\n----------------------------------------------------------------------')
    print('Doing a search with the following data:\n'
          '\n            key: {}'
          '\n    environment: {}'
          '\n     Expect to find the value: \'{}\'\n'.format(key_name, env, exp_value_data))

# Searching for a key within the file 'RedHat.yaml'.

key_name = 'sshservicename'
os = 'RedHat'
env = 'osfamily=\'{}\''.format(os)
exp_value_data = 'sshd'

print_test_info(key_name, env, exp_value_data)
req = hiera.HieraClient(HIERA_CONFIG_FILE, osfamily='{}'.format(os))
ret = req.get(key_name)

if req is not None and ret == exp_value_data:
    print('Received data from hiera call: \'{}\'\n'
          'Success!'.format(req.get(key_name)))
else:
    EXITCODE='1'
    print('!!! Uhh, that went wrong!!! Got return value: \'{}\''.format(ret))
print('\n----------------------------------------------------------------------')

# Searching for a key within the file 'Debian.yaml'.

os = 'Debian'
env = 'osfamily=\'{}\''.format(os)
exp_value_data = 'ssh'

print_test_info(key_name, env, exp_value_data)
req = hiera.HieraClient(HIERA_CONFIG_FILE, osfamily='{}'.format(os))
ret = req.get(key_name)

if req is not 'None' and ret == exp_value_data:
    print('Received data from hiera call: \'{}\'\n'
          'Success!'.format(req.get(key_name)))
else:
    EXITCODE='1'
    print('!!! Uhh, that went wrong! Got return value: \'{}\''.format(ret))
print('\n----------------------------------------------------------------------')

# Searching for a subkey within 'common.yaml'.

key_name = 'default_layer1.subject'
exp_value_data = 'Data for default_layer1'
env = ''

print_test_info(key_name, env, exp_value_data)
req = hiera.HieraClient(HIERA_CONFIG_FILE)
ret = req.get(key_name)

if req is not None and ret == exp_value_data:
    print('Received data from hiera call: \'{}\'\n'
          'Success!'.format(req.get(key_name)))
else:
    EXITCODE='1'
    print('!!! Uhh, that went wrong! Got return value: \'{}\''.format(ret))
print('\n----------------------------------------------------------------------')

# Searching for an non-existing key.

key_name = 'not-existing'
os = 'Debian'
env = 'osfamily=\'{}\''.format(os)
exp_value_data = 'None'

print_test_info(key_name, env, exp_value_data)
req = hiera.HieraClient(HIERA_CONFIG_FILE, osfamily='{}'.format(os))
ret = req.get(key_name)

if ret is None:
    print('Received data from hiera call: \'{}\'\n'
          'Success!'.format(req.get(key_name)))
else:
    EXITCODE='1'
    print('!!! Uhh, that went wrong! Got return value: \'{}\''.format(ret))
print('\n----------------------------------------------------------------------')

if EXITCODE is not '0':
    sys.exit(1)

