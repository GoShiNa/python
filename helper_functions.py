"""     4/11/2017, 3:15 PM    """
__author__ = "Motti Javare Gowda G H"

import Queue, json, os, collections, errno, random
import sys, pysftp, uuid
from mysql.connector import MySQLConnection, Error, DataError

from response.config.mysqlConfig import read_mysqldb_config

def execute_query(q):
    db_config = read_mysqldb_config()
    conn = MySQLConnection(**db_config)
    cursor = conn.cursor(buffered=True)
    try:
        me = []
        cursor.execute(q)
        for r in cursor:
            me.append(r)
        return me
    except Error as error:
        print error
    finally:
        conn.commit()
        cursor.close()
        conn.close()


def get_records(name):
    db_config = read_mysqldb_config()
    conn = MySQLConnection(**db_config)
    cursor = conn.cursor(buffered=True)
    check_for_availability = "select instance_id, vm_name, ip_address, vm_status from emu_response where vm_name='%s'"
    try:
        me = []
        cursor.execute(check_for_availability % (name))
        for r in cursor:
            me.append(r)
        return me[0]
    except Error as error:
        print error
    finally:
        conn.commit()
        cursor.close()
        conn.close()

def validate_name(name):
    db_config = read_mysqldb_config()
    conn = MySQLConnection(**db_config)
    cursor = conn.cursor(buffered=True)
    check_for_availability = "select count(*) from emu_response where vm_name='%s'"
    try:
        me = []
        cursor.execute(check_for_availability % (name))
        for r in cursor:
            me.append(r)
        return me[0][0]
    except Error as error:
        print error
    finally:
        conn.commit()
        cursor.close()
        conn.close()


def sftp_files(hostpath, local_dir):
    #hostpath = '/root/gowda/tmp'
    print hostpath
    localpath = '/home/css/emulator/response/' + local_dir + 'output.txt'
	print localpath
    
    try:
    	with pysftp.Connection('192.168.20.137', username='root', password='deployment123') as sftp:
          sftp.put(localpath, hostpath)
    except Exception as e:
        print e
        raise e
    print 'Success: File transferred from server 192.168.20.217 to 192.168.20.137 ---'


def create_dir_file(directory):
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise


def write_to_file(direct, data):
    direct = direct + 'output.txt'
    with open(direct, "a+") as app:
        for i in range(len(data)):
            record = [n.strip() for n in data[i]]
            record = "   ".join(record)
            app.write(record + '\n')


def isNotEmpty(strr):
    #print 'Input : ', strr
    return bool(strr and strr.strip())


def find_read_instances(instancename):
    data = {}
    if instancename == "aws":
        data = open_ip_pool_file("config/aws.txt")
    elif instancename == "azure":
        data = open_ip_pool_file("config/azure.txt")
    elif instancename == "openstack":
        data = open_ip_pool_file("config/openstack.txt")
    elif instancename == "vmware":
        data = open_ip_pool_file("config/vmware.txt")
    return data


def open_ip_pool_file(myFile):
    data = {}
    with open(myFile) as inFile:
        data = inFile.read().split('\n')
    return data


def read_ip(instancename):
    data = find_read_instances(instancename)
    q = Queue.Queue()
    for item in data:
        q.put(item)
    return q


def read_json_template(jsonFileName):
    ''' 
    function to read the json and load it to Python object
    Used with - open - as, to safely open and close the Json file
    '''
    with open(jsonFileName) as json_file:
        loadedData = json.load(json_file)
        return loadedData


def update_response(adict, k, v):
    ''' 
    Function to read the JSON file according to their tuple, list or dict
    using (key, value) pair we can search the k, v in json and update
    '''
    for key in adict.keys():
        if key == k:
            adict[key] = v
        elif type(adict[key]) is dict:
            update_response(adict[key], k, v)
        elif type(adict[key]) is list:
            for elm in adict[key]:
                if k in elm:
                    elm[k] = v

def getUUID():
    return str(uuid.uuid4())

def _send(socket, data):
    try:
        serialized = json.dumps(data)
    except (TypeError, ValueError), e:
        raise Exception('You can only send JSON-serializable data')
    # send the length of the serialized data first
    # print 'Client %r' % socket
    socket.send('%d\n' % len(serialized))
    # send the serialized data
    socket.sendall(serialized)


def _recv(socket):
    # read the length of the data, letter by letter until we reach EOL
    length_str = ''
    char = socket.recv(1)
    while char != '\n':
        length_str += char
        char = socket.recv(1)
    total = int(length_str)
    # use a memoryview to receive the data chunk by chunk efficiently
    view = memoryview(bytearray(total))
    next_offset = 0
    while total - next_offset > 0:
        recv_size = socket.recv_into(view[next_offset:], total - next_offset)
        next_offset += recv_size
    try:
        deserialized = json.loads(view.tobytes())
    except (TypeError, ValueError), e:
        raise Exception('Data received was not in JSON format')
    return deserialized






#   ********************************************************************************    #
## New file --- May be used later

def update_Q_file(fileToClose, q):
    print 'Queue size --- ' + str(q.qsize())
    with open(fileToClose, 'w+') as output:
        for val in range(q.qsize()):
            v = q.get()
            print v
            output.write(v + "\n")
        print 'File Overwrote'

def get_mac():
    mac = [0x00, 0x16, 0x3e,
           random.randint(0x00, 0x7f),
           random.randint(0x00, 0xff),
           random.randint(0x00, 0xff)]
    return ':'.join(map(lambda x: "%02x" % x, mac))

'''
## This is from newService
        cloud_id = "ca554092-3c06-420f-9124-eee5bdab9898"
        template = obj.get_response_template()
        newObj = obj.update_response_template(template, newList)
        try:
            path = coms.create_new_dir(provider, ip)  # Store the Response in a file
            coms.create_a_file(path, newObj)
        except IOError as e:
            print e
'''

def create_new_dir(provider, ip):
    newPath = 'newInstance/' + provider + str(ip) + '.json'
    return newPath


def create_a_file(newPath, data):
    with open(newPath, 'w') as outfile:
        json.dump(data, outfile, sort_keys=True, indent=4,
                  ensure_ascii=False)

### Not Using right now###
#For future Use#

def check_for_filename(ip):
    for root, dirs, file in os.walk('newInstance/'):
        pass
    fi = [sub for sub in file if str(ip) in sub]
    print fi
    if len(fi) > 0:  # != 0
        fi = fi.pop(0)
        print fi
        return 'newInstance/' + fi
    else:
        return None


def delete_a_file(path, ip):
    print 'Decommissioning ' + str(ip)
    try:
        os.remove(path)
    except IOError as err:
        print err

def convert_keys_to_string(dictionary):
    """Recursively converts dictionary keys to strings."""
    if not isinstance(dictionary, dict):
        return dictionary
    return dict((str(k), convert_keys_to_string(v))
                for k, v in dictionary.items())


def unicodeTostring(data):
    if isinstance(data, basestring):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(unicodeTostring, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(unicodeTostring, data))
    else:
        return data
        
        
def to_str(key, value):
    if isinstance(key, unicode):
        key = str(key)
    if isinstance(value, unicode):
        value = str(value)
    return key, value
