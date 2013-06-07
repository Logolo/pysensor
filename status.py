#!/usr/bin/python
import sys, os
import time
from pprint import pprint as pp
import unicodedata
from inspect import isfunction

print "importing psutil"
import psutil
print "importing zmq"
import zmq
print "importing netifaces"
import netifaces

print "importing sqlalchemy"
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm				import sessionmaker, relationship, backref
from sqlalchemy					import Column, Integer, String, Float, ForeignKey, ForeignKeyConstraint
from sqlalchemy					import create_engine, Sequence
Base            = declarative_base()
print "finished importing"

test       = False
numReport  = -2
myNameFile = '.status'
db_path    = 'sqlite:///status.db'
# db_path  = 'sqlite:///:memory:'


#apt-get install sqlite3
#apt-get install python-pip
#apt-get install python-dev
#apt-get install libzmq-dev

#easy_install pysqlite
#easy_install SQLAlchemy
#easy_install psutil
#easy_install netifaces
#easy_install pyzmq

#NOT NECESSARY
#apt-get install python-sqlalchemy
#apt-get install python-sqlite

utime  = time.time()
myName = None

forbidden = ['data_structure', 'metadata']




def get_fields(self):
	# print "table name", self.__table__
	keys = []
	for x in dir( self ):
		if x[0] == '_'                : continue
		if x in forbidden             : continue
		y = getattr(self, x)
		if hasattr(y, '__call__')     : continue
		if isfunction(y)              : continue
		if '__main__.' in str(type(y)): continue
		
		# <class 'sqlalchemy.orm.collections.InstrumentedList'>
		
		# print "x",x,"t",type(y)
		keys.append(x)
		
	# print [ x for x in dir( self.__table__ ) if x[0] != '_' ]
	# print self.__table__.columns
	# print "self table"          , self.__table__
	# print "self table dir self" , dir( self           )
	# print "self table dir table", dir( self.__table__ )
	# print "self table columns"  , self.__table__.columns
	# print "self table descript" , self.__table__.description
	# print "self table foreign"  , self.__table__.foreign_keys
	#print "self table children" , self.__table__.get_children()
	# print "self table info"     , self.__table__.info
	# print "self table schema"   , self.__table__.schema
	
	# print keys, "\n"
	return keys

def get_dict(self):
	res = {}
	
	for key in self.get_fields():
		val = getattr( self, key )
		
		if str(type( val )) == "<class 'sqlalchemy.orm.state.InstanceState'>":
			continue

		if str(type( val )) == "<class 'sqlalchemy.orm.collections.InstrumentedList'>":
			valt = []
			for v in val:
				valt.append( v.get_dict() )
			val  = valt

		elif str(type( val )) == "<type 'unicode'>":
			# print "fixing unicode"
			val  = unicodedata.normalize('NFKD', val).encode('ascii','ignore')

		else:
			#print str(type( val ))
			pass
		
		res[ key ] = val
	
	return res

Base.get_fields = get_fields
Base.get_dict   = get_dict

class Memory(Base):
	__tablename__ = 'mem'
	ltime     = Column(Float      , primary_key=True)
	my_name   = Column(String(17 ), primary_key=True)
	__table_args__ = (
		ForeignKeyConstraint( ['ltime', 'my_name'], ['data_structure.ltime', 'data_structure.my_name'] ),
	)
	
	total     = Column(Integer    )
	available = Column(Integer    )
	percent   = Column(Float      )
	used      = Column(Integer    )
	free      = Column(Integer    )
	active    = Column(Integer    )
	inactive  = Column(Integer    )
	buffers   = Column(Integer    )
	cached    = Column(Integer    )

	def __init__(self, *args):
		if	 len(args) == 11:
			self.init_base(*args)

		elif len(args) == 0:
			self.init_self(*args)

		else:
			print "wrong number of arguments: %d" % len(args)
			sys.exit( 1 )

	def init_self(self):
		# print "init_self"
		vmem           = psutil.virtual_memory()
		#vmem(total=392007680L, available=129564672L, percent=66.9, used=381054976L, 
		#free=10952704L, active=171753472, inactive=182312960, buffers=23056384L, cached=95555584)
		self.ltime     = utime
		self.my_name   = myName
		self.total     = vmem.total
		self.available = vmem.available
		self.percent   = vmem.percent
		self.used      = vmem.used
		self.free      = vmem.free
		self.active    = vmem.active
		self.inactive  = vmem.inactive
		self.buffers   = vmem.buffers
		self.cached    = vmem.cached

	def init_base(self, ltime, my_name, total, available, percent, used, free, active, inactive, buffers, cached):
		# print "init_base %f %d %d" % (ltime, free, used)
		self.ltime     = ltime
		self.my_name   = my_name
		self.total     = total
		self.available = available
		self.percent   = percent
		self.used      = used
		self.free      = free
		self.active    = active
		self.inactive  = inactive
		self.buffers   = buffers
		self.cached	   = cached

	def __repr__(self):
		return "<Memory('%f', '%s', '%d', '%d', '%f', '%d', '%d', '%d', '%d', '%d', '%d')>" % ( self.ltime, self.my_name, self.total, self.available, self.percent, self.used, self.free, self.active, self.inactive, self.buffers, self.cached )

class Cpu(Base):
	__tablename__ = 'cpu'
	ltime     = Column(Float      , primary_key=True)
	my_name   = Column(String(17 ), primary_key=True)
	__table_args__ = (
		ForeignKeyConstraint( ['ltime', 'my_name'], ['data_structure.ltime', 'data_structure.my_name'] ),
	)
	
	
	user      = Column(Float      )
	nice      = Column(Float      )
	system    = Column(Float      )
	idle      = Column(Float      )
	iowait    = Column(Float      )
	irq       = Column(Float      )
	softirq   = Column(Float      )
	numCpu    = Column(Integer    )
	cpuPerc   = Column(String     )

	def __init__(self, *args):
		if	 len(args) == 12:
			self.init_base(*args)

		elif len(args) == 0:
			self.init_self(*args)

		else:
			print "wrong number of arguments: %d" % len(args)
			sys.exit( 1 )

	def init_self(self):
		# print "init_self"
		cputimes      = psutil.cpu_times()
		numCpu        = psutil.NUM_CPUS
		cpuPerc       = psutil.cpu_percent(percpu=True)
		cpuPerc       = ",".join([str(x) for x in cpuPerc])
		#cputimes(user=3961.46, nice=169.729, system=2150.659, idle=16900.540, iowait=629.509, irq=0.0, softirq=19.422)
		
		self.ltime     = utime
		self.my_name   = myName
		self.user      = cputimes.user
		self.nice      = cputimes.nice
		self.system    = cputimes.system
		self.idle      = cputimes.idle
		self.iowait    = cputimes.iowait
		self.irq       = cputimes.irq
		self.softirq   = cputimes.softirq
		self.numCpu    = numCpu
		self.cpuPerc   = cpuPerc

	def init_base(self, ltime, my_name, user, nice, system, idle, iowait, irq, softirq, numCpu, cpuPerc):
		# print "init_base %f %f %f %f %f %f %f %f %d" % (ltime, user, nice, system, idle, iowait, irq, softirq, numCpu, cpuPerc)
		self.ltime     = ltime
		self.my_name   = my_name
		self.user      = user
		self.nice      = nice
		self.system    = system
		self.idle      = idle
		self.iowait    = iowait
		self.irq       = irq
		self.softirq   = softirq
		self.numCpu    = numCpu
		self.cpuPerc   = cpuPerc

	def __repr__(self):
		return "<CPU('%f', '%s', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%d', '%s')>" % ( self.ltime, self.my_name, self.user, self.nice, self.system, self.idle, self.iowait, self.irq, self.softirq, self.numCpu, self.cpuPerc )

class Disk(Base):
	__tablename__ = 'disk'
	ltime	      = Column(Float      , primary_key=True)
	my_name       = Column(String(17 ), primary_key=True)
	__table_args__ = (
		ForeignKeyConstraint( ['ltime', 'my_name'], ['data_structure.ltime', 'data_structure.my_name'] ),
	)
	
	read_count    = Column(Integer    )
	write_count   = Column(Integer    )
	read_bytes    = Column(Integer    )
	write_bytes   = Column(Integer    )
	read_time     = Column(Integer    )
	write_time    = Column(Integer    )
	partitions    = relationship('Disk_partition', backref='disk', order_by='Disk_partition.mountpoint')
	
	def __init__(self, *args):
		if	 len(args) == 9:
			self.init_base(*args)

		elif len(args) == 0:
			self.init_self(*args)

		else:
			print "wrong number of arguments: %d" % len(args)
			sys.exit( 1 )

	def init_self(self):
		# print "init_self"
		
		partitions = psutil.disk_partitions()
		for partition in sorted(partitions, key=lambda x:x.device):
			#partition(device='/dev/sda1', mountpoint='/', fstype='ext4')
			usage = psutil.disk_usage(partition.mountpoint)
			#usage(total=21378641920, used=4809781248, free=15482871808, percent=22.5)

			self.partitions.append( Disk_partition(	utime, 					myName,
													partition.device,		partition.mountpoint,
													partition.fstype,		usage.total,
													usage.used,				usage.free,
													usage.percent) )
		
		diskio		       = psutil.disk_io_counters()
		#iostat(read_count=719566, write_count=1082197, read_bytes=18626220032, write_bytes=24081764352, read_time=5023392, write_time=63199568)
		self.ltime         = utime
		self.my_name       = myName
		self.read_count    = diskio.read_count
		self.write_count   = diskio.write_count
		self.read_bytes    = diskio.read_bytes
		self.write_bytes   = diskio.write_bytes
		self.read_time     = diskio.read_time
		self.write_time    = diskio.write_time
		
		#print "GET FIELDS", self.get_dict()

	def init_base(self, ltime, my_name, read_count, write_count, read_bytes, write_bytes, read_time, write_time, partitions):
		# print "init_base %f " % (ltime)
		self.ltime         = ltime
		self.my_name       = my_name
		self.read_count    = read_count
		self.write_count   = write_count
		self.read_bytes    = read_bytes
		self.write_bytes   = write_bytes
		self.read_time     = read_time
		self.write_time    = write_time
		self.partitions    = partitions

	def __repr__(self):
		return "<DISK('%f', '%s', '%d', '%d', '%d', '%d', '%d', '%d', '%s')>" % ( self.ltime, self.my_name, self.read_count, self.write_count, self.read_bytes, self.write_bytes, self.read_time, self.write_time, str(self.partitions) )

class Disk_partition(Base):
	__tablename__ = 'disk_partition'
	# id            = Column(Integer    , primary_key=True)
	ltime	      = Column(Float      , primary_key=True)
	my_name       = Column(String(17 ), primary_key=True)
	__table_args__ = (
		ForeignKeyConstraint( ['ltime', 'my_name'], ['disk.ltime', 'disk.my_name'] ),
	)
	
	device        = Column(String     , primary_key=True)
	mountpoint    = Column(String     )
	fstype        = Column(String     )
	total         = Column(Integer    )
	used          = Column(Integer    )
	free          = Column(Integer    )
	percent       = Column(Float      )

	def __init__(self, ltime, my_name, device, mountpoint, fstype, total, used, free, percent):
		# print "init_base %f " % (ltime)
		self.ltime         = ltime
		self.my_name       = my_name
		self.device        = device
		self.mountpoint    = mountpoint
		self.fstype        = fstype
		self.total         = total
		self.used          = used
		self.free          = free
		self.percent       = percent

	def __repr__(self):
		# print ( self.id, self.ltime, self.device, self.mountpoint, self.fstype, self.total, self.used, self.free, self.percent )
		return "<DISKPARTITION('%s', '%f', '%s', '%s', '%s', '%d', '%d', '%d', '%f')>" % ( str(self.id), self.ltime, self.device, self.mountpoint, self.fstype, self.total, self.used, self.free, self.percent )

class Network_devices(Base):
	__tablename__ = 'network_devices'
	ltime         = Column(Float      , primary_key=True)
	my_name       = Column(String(17 ), primary_key=True)
	__table_args__ = (
		ForeignKeyConstraint( ['ltime', 'my_name'], ['data_structure.ltime', 'data_structure.my_name'] ),
	)
	
	dev_name      = Column(String     , primary_key=True)
	bytes_sent    = Column(Integer    )
	bytes_recv    = Column(Integer    )
	packets_sent  = Column(Integer    )
	packets_recv  = Column(Integer    )
	errin         = Column(Integer    )
	errout        = Column(Integer    )
	dropin        = Column(Integer    )
	dropout       = Column(Integer    )
	mac           = Column(String(17 ))
	ip            = Column(String(15 ))

	def __init__(self, 	ltime, 			my_name,		dev_name, 
						bytes_sent, 	bytes_recv, 
						packets_sent, 	packets_recv, 
						errin, 			errout, 
						dropin, 		dropout,
						mac,			ip):
		# {'lo' : iostat(bytes_sent=799953745, bytes_recv=799953745 , packets_sent=453698 , packets_recv=453698 , errin=0, errout=0, dropin=0, dropout=0), 
		# print "init_base %f " % (ltime)
		self.ltime        = ltime
		self.my_name      = my_name
		self.dev_name     = dev_name
		self.bytes_sent   = bytes_sent
		self.bytes_recv   = bytes_recv
		self.packets_sent = packets_sent
		self.packets_recv = packets_recv
		self.errin        = errin
		self.errout       = errout
		self.dropin       = dropin
		self.dropout      = dropout
		self.mac          = mac
		self.ip           = ip

	def __repr__(self):
		return "<NETWORKDEVICES('%d', '%f', '%s', '%s', '%d', '%d', '%d', '%d', '%d', '%d', '%d', '%d', '%s', '%s')>" % ( self.id, self.ltime, self.my_name, self.dev_name, self.bytes_sent, self.bytes_recv, self.packets_sent, self.packets_recv, self.errin, self.errout, self.dropin, self.dropout, self.mac, self.ip )

class Process_info(Base):
	__tablename__           = 'process_info'
	ltime                   = Column(Float      , primary_key=True)
	my_name                 = Column(String(17 ), primary_key=True)
	__table_args__ = (
		ForeignKeyConstraint( ['ltime', 'my_name'], ['data_structure.ltime', 'data_structure.my_name'] ),
	)
	
	procnum                 = Column(Integer    , primary_key=True)
	name                    = Column(String     )
	exe                     = Column(String     )
	cwd                     = Column(String     )
	cmdline                 = Column(String     )
	status                  = Column(Integer    )
	username                = Column(String     )
	create_time             = Column(Float      )
	uids_real               = Column(Integer    )
	uids_effective          = Column(Integer    )
	uids_saved              = Column(Integer    )
	gids_real               = Column(Integer    )
	gids_effective          = Column(Integer    )
	gids_saved              = Column(Integer    )
	cpu_times_user          = Column(Float      )
	cpu_times_system        = Column(Float      )
	cpu_affinity            = Column(String     )
	memory_percent          = Column(Float      )
	mem_info_rss            = Column(Integer    )
	mem_info_vms            = Column(Integer    )
	mem_info_shared         = Column(Integer    )
	mem_info_text           = Column(Integer    )
	mem_info_lib            = Column(Integer    )
	mem_info_data           = Column(Integer    )
	mem_info_dirty          = Column(Integer    )
	io_counters_read_count  = Column(Integer    )
	io_counters_write_count = Column(Integer    )
	io_counters_read_bytes  = Column(Integer    )
	io_counters_write_bytes = Column(Integer    )
	nice                    = Column(Integer    )
	num_threads             = Column(Integer    )
	num_fds                 = Column(Integer    )


	def __init__(self,	ltime,						my_name,					procnum,
						name,						exe,						cwd,
						cmdline,					status,						username,
						create_time,				uids_real,					uids_effective,
						uids_saved,					gids_real,					gids_effective,
						gids_saved,					cpu_times_user,				cpu_times_system,
						cpu_affinity,				memory_percent,				mem_info_rss,
						mem_info_vms,				mem_info_shared,			mem_info_text,
						mem_info_lib,				mem_info_data,				mem_info_dirty,
						io_counters_read_count,		io_counters_write_count,	io_counters_read_bytes,
						io_counters_write_bytes,	nice,						num_threads,
						num_fds
						):

		self.procnum                 = procnum
		self.my_name                 = my_name
		self.name                    = name
		self.exe                     = exe
		self.cwd                     = cwd
		self.cmdline                 = cmdline
		self.status                  = status
		self.username                = username
		self.create_time             = create_time
		self.uids_real               = uids_real
		self.uids_effective          = uids_effective
		self.uids_saved              = uids_saved
		self.gids_real               = gids_real
		self.gids_effective          = gids_effective
		self.gids_saved              = gids_saved
		self.cpu_times_user          = cpu_times_user
		self.cpu_times_system        = cpu_times_system
		self.cpu_affinity            = cpu_affinity
		self.memory_percent          = memory_percent
		self.mem_info_rss            = mem_info_rss
		self.mem_info_vms            = mem_info_vms 
		self.mem_info_shared         = mem_info_shared
		self.mem_info_text           = mem_info_text
		self.mem_info_lib            = mem_info_lib
		self.mem_info_data           = mem_info_data
		self.mem_info_dirty          = mem_info_dirty
		self.io_counters_read_count  = io_counters_read_count
		self.io_counters_write_count = io_counters_write_count
		self.io_counters_read_bytes  = io_counters_read_bytes
		self.io_counters_write_bytes = io_counters_write_bytes
		self.nice                    = nice
		self.num_threads             = num_threads
		self.num_fds                 = num_fds

	def __repr__(self):
		res_str = []
		for val in 	self.id,						self.ltime,\
					self.my_name,					self.procnum,\
					self.name,						self.exe,						self.cwd,\
					self.cmdline,					self.status,					self.username,\
					self.create_time,				self.uids_real,					self.uids_effective,\
					self.uids_saved,				self.gids_real,					self.gids_effective,\
					self.gids_saved,				self.cpu_times_user,			self.cpu_times_system,\
					self.cpu_affinity,				self.memory_percent,			self.mem_info_rss,\
					self.mem_info_vms,				self.mem_info_shared,			self.mem_info_text,\
					self.mem_info_lib,				self.mem_info_data,				self.mem_info_dirty,\
					self.io_counters_read_count,	self.io_counters_write_count,	self.io_counters_read_bytes,\
					self.io_counters_write_bytes,	self.nice,						self.num_threads,\
					self.num_fds:
			try:
				res_str.append( "'%s'" % val )
			except:
				try:
					res_str.append( "'%f'" % val )
				except:
					res_str.append( "'%d'" % val )
			
		return "<PROCESSINFO(%s)>" % ( " ".join( res_str ) )

class Data_structure(Base):
	__tablename__ = 'data_structure'

	ltime         = Column(Float      , primary_key=True)
	my_name       = Column(String(17 ), primary_key=True)

	#primaryjoin=(ltime==Memory.ltime), secondaryjoin=(my_name==Memory.my_name), , foreignkeys=Memory.ltime
	# primaryjoin=ltime==Memory.ltime, secondaryjoin=(my_name==Memory.my_name),
	memories      = relationship('Memory'         , backref='data_structure', order_by="Memory.ltime"         )
	cpus          = relationship('Cpu'            , backref='data_structure', order_by="Cpu.ltime"            )
	disks         = relationship('Disk'           , backref='data_structure', order_by="Disk.ltime"           )
	net_devices   = relationship('Network_devices', backref='data_structure', order_by="Network_devices.ltime")
	process_info  = relationship('Process_info'   , backref='data_structure', order_by="Process_info.ltime"   )
	# processes     = relationship('Process'        , backref='data_structure', order_by="Process.ltime")
	# networks      = relationship('Network'        , backref='data_structure', order_by="Network.ltime")

	def __init__(self, *args):
		if	 len(args) == 7:
			self.init_base(*args)

		elif len(args) == 0:
			self.init_self(*args)

		else:
			print "wrong number of arguments: %d" % len(args)
			sys.exit( 1 )

	def init_self(self):
		self.ltime    = utime
		self.my_name  = myName

		self.memories.append(  Memory()  )
		self.cpus.append(      Cpu()     )
		self.disks.append(     Disk()    )
		# self.networks.append(  Network() )
		# self.processes.append( Process() )
		self.Network()
		self.Process()
		
	def init_base(self, ltime, my_name, lmemories, lcpus, ldisks, lnetworks, lprocesses):
		# print "init_base %f %s" % (ltime, net_devices)
		self.ltime     = ltime
		self.my_name   = my_name
		self.memories  = lmemories
		self.cpus      = lcpus
		self.disks     = ldisks
		self.networks  = lnetworks
		self.processes = lprocesses

	def get_fields(self):
		# return self.__dict__.keys()
		# return ['ltime', 'my_name', 'memories', 'cpus', 'disks', 'networks', 'processes']
		return ['ltime', 'my_name', 'memories', 'cpus', 'disks', 'net_devices', 'process_info']
	
	def Network(self):
		# print "init_self"

		nets   = psutil.network_io_counters(pernic=True)
		# {'lo' : iostat(bytes_sent=799953745, bytes_recv=799953745 , packets_sent=453698 , packets_recv=453698 , errin=0, errout=0, dropin=0, dropout=0), 
		# 'eth0': iostat(bytes_sent=734324837, bytes_recv=4163935363, packets_sent=3605828, packets_recv=4096685, errin=0, errout=0, dropin=0, dropout=0)}
		
		
		for net in sorted(nets):
			netdata = nets[ net ]
			
			ifdata  = netifaces.ifaddresses(net)
			mac     = ifdata[netifaces.AF_LINK][0]['addr']
			ip      = ifdata[2                ][0]['addr']
			
			nd = Network_devices( 	utime				, myName,
									net,
									netdata.bytes_sent  , netdata.bytes_recv, 
									netdata.packets_sent, netdata.packets_recv, 
									netdata.errin       , netdata.errout, 
									netdata.dropin      , netdata.dropout,
									mac					, ip)
			self.net_devices.append( nd )
	
	def Process(self):
		# print "init_self"
		pces   = psutil.get_pid_list()
		# [1, 2, 3, 4, 5, 6, 7, 46
		
		for procnum in sorted(pces):
			try:
				procinfo                = psutil.Process(procnum)
			except:
				continue
			
			name                    = procinfo.name
			
			try:
				exe                 = procinfo.exe
			except:
				exe                 = ""
				
			try:
				cwd                 = procinfo.getcwd()
			except:
				cwd                 = ""
				
			cmdline                 = procinfo.cmdline
			cmdline                 = " ".join( cmdline )
			status                  = procinfo.status
			username                = procinfo.username
			create_time             = procinfo.create_time
			uids                    = procinfo.uids
			uids_real               = uids.real
			uids_effective          = uids.effective
			uids_saved              = uids.saved
			gids                    = procinfo.gids
			gids_real               = gids.real
			gids_effective          = gids.effective
			gids_saved              = gids.saved
			cpu_times               = procinfo.get_cpu_times()
			cpu_times_user          = cpu_times.user
			cpu_times_system        = cpu_times.system
			cpu_affinity            = procinfo.get_cpu_affinity()
			cpu_affinity            = ",".join([ str(x) for x in cpu_affinity])
			memory_percent          = procinfo.get_memory_percent()
			mem_info                = procinfo.get_ext_memory_info()
			mem_info_rss            = mem_info.rss
			mem_info_vms            = mem_info.vms
			mem_info_shared         = mem_info.shared
			mem_info_text           = mem_info.text
			mem_info_lib            = mem_info.lib
			mem_info_data           = mem_info.data
			mem_info_dirty          = mem_info.dirty
			
			try:
				io_counters              = procinfo.get_io_counters()
				io_counters_read_count   = io_counters.read_count
				io_counters_write_count  = io_counters.write_count
				io_counters_read_bytes   = io_counters.read_bytes
				io_counters_write_bytes  = io_counters.write_bytes
				
			except:
				io_counters_read_count   = 0
				io_counters_write_count  = 0
				io_counters_read_bytes   = 0
				io_counters_write_bytes  = 0
			
			nice                         = procinfo.get_nice()
			num_threads                  = procinfo.get_num_threads()
			
			try:
				num_fds                  = procinfo.get_num_fds()
			except:
				num_fds                  = 0

			# num_ctx_switches             = procinfo.get_num_ctx_switches()
			# num_ctx_switches_voluntary   = num_ctx_switches.voluntary
			# num_ctx_switches_involuntary = num_ctx_switches.involuntary

			# try:
				# open_files               = procinfo.get_open_files()
				# open_files_path          = open_files.path
				# open_files_fd            = open_files.fd
			# except:
				# open_files_path          = ""
				# open_files_fd            = ""

			# p.get_connections()
			# [connection(fd=115, family=2, type=1, local_address=('10.0.0.1', 48776),
            # remote_address=('93.186.135.91', 80), status='ESTABLISHED'),

			# threads             = procinfo.get_threads()
			# threads_id          = thread
			# threads_user_time   = user_time
			# threads_system_time = system_time
			
			
			pi = Process_info(	utime, 						myName,						procnum,
								name,						exe,						cwd,
								cmdline,					status,						username,
								create_time,				uids_real,					uids_effective,
								uids_saved,					gids_real,					gids_effective,
								gids_saved,					cpu_times_user,				cpu_times_system,
								cpu_affinity,				memory_percent,				mem_info_rss,
								mem_info_vms,				mem_info_shared,			mem_info_text,
								mem_info_lib,				mem_info_data,				mem_info_dirty,
								io_counters_read_count,		io_counters_write_count,	io_counters_read_bytes,
								io_counters_write_bytes,	nice,						num_threads,
								num_fds
								)
			self.process_info.append(pi)
	
	def __repr__(self):
		return "<DATASTRUCT('%f', '%s', '%s', '%s', '%s', '%s', '%s')>" % ( self.ltime, self.my_name, self.memories, self.cpus, self.disks, self.networks, self.processes )

class DataManager(object):
	def __init__(self, numReport, echo=False):
		self.numReport = numReport
		print "      DataManager: loading engine"
		self.engine    = create_engine( db_path, echo=echo )
		
		print "      DataManager: creating database"
		Base.metadata.create_all(       self.engine     )
		
		print "      DataManager: creating session"
		self.Session    = sessionmaker( bind=self.engine )
		
		print "      DataManager: initializing session"
		self.session    = self.Session()
		
		self.data       = None
		self.qry        = None
	
	def update(self):
		global utime
		utime     = time.time()
		
		print "      DataManager: utime", utime, time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
		print "      DataManager: creating data structure"
		self.data = Data_structure()
		print "      DataManager: adding data"
		self.session.add( self.data )
		print "      DataManager: commiting"
		self.session.commit()
		print "      DataManager: done"

	def load(self, reps=None):
		if reps is None:
			reps = self.numReport
		
		print "      DataManager: querying"
		self.qry = self.session.query( Data_structure ).order_by( Data_structure.ltime )[reps:]
		print "      DataManager: done"
		
		return self.qry

	def get_dict(self):
		self.load()
		res = []
		for qry in self.qry:
			# print "qry", qry
			r = qry.get_dict()
			# print "  ", r
			res.append( r )
		return res

def getName():
	if not os.path.exists(myNameFile):
		nets   = psutil.network_io_counters(pernic=True)
		# {'lo' : iostat(bytes_sent=799953745, bytes_recv=799953745 , packets_sent=453698 , packets_recv=453698 , errin=0, errout=0, dropin=0, dropout=0), 
		# 'eth0': iostat(bytes_sent=734324837, bytes_recv=4163935363, packets_sent=3605828, packets_recv=4096685, errin=0, errout=0, dropin=0, dropout=0)}
		
		mac = None
		for net in sorted(nets):
			netdata = nets[ net ]
			
			ifdata = netifaces.ifaddresses(net)
			mac    = ifdata[netifaces.AF_LINK][0]['addr']
			if mac != '00:00:00:00:00:00':
				break
		
		if mac is None:
			print "NO MAC FOUND"
			sys.exit( 1 )
		
		with open(myNameFile, 'w') as fhd:
			fhd.write(mac)
	
	mac = None
	with open(myNameFile, 'r') as fhd:
		mac = fhd.read()
	
	if mac is None or len(mac) != 17:
		print "not able to get MAC", mac
		sys.exit(1)
		
	return mac

def main():
	#http://docs.sqlalchemy.org/en/rel_0_8/orm/tutorial.html
	
	global myName
	print "  getting name"
	myName = getName()
	print "  name:", myName
	
	print "  initializing"
	data   = DataManager(numReport)
	
	print "  gathering data"
	
	if test:
		for i in range(4):
			print "    adding",i
			data.update()
			
	else:
		print "    adding"
		data.update()


	if test:
		print "    loading"
		res = data.get_dict()
		print "    printing"
		pp( res )
	
	print "  done\n"



if __name__ == "__main__": 
	if   __file__ in [ 'client.py', 'status.py' ]:
		print "calling client main"
		main()
	elif __file__ in [ 'server.py' ]:
		#http://zguide.zeromq.org/py:all
		#http://zguide.zeromq.org/py:taskwork
		#http://zguide.zeromq.org/py:tasksink
		#https://github.com/imatix/zguide/tree/master/examples/Python


		print "importing net"
		import sys
		import time
		import zmq
		import socket
		PING_PORT_NUMBER = 9999
		PING_MSG_SIZE    = 1
		PING_INTERVAL    = 1  # Once per second

		class UDP(object):
			"""simple UDP ping class"""
			handle = None   # Socket for send/recv
			port = 0        # UDP port we work on
			address = ''    # Own address
			broadcast = ''  # Broadcast address

			def __init__(self, port, address=None, broadcast=None):
				if address is None:
					local_addrs = socket.gethostbyname_ex(socket.gethostname())[-1]
					for addr in local_addrs:
						if not addr.startswith('127'):
							address = addr
				if broadcast is None:
					broadcast = '255.255.255.255'

				self.address = address
				self.broadcast = broadcast
				self.port = port
				# Create UDP socket
				self.handle = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

				# Ask operating system to let us do broadcasts from socket
				self.handle.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

				# Bind UDP socket to local port so we can receive pings
				self.handle.bind(('', port))

			def send(self, buf):
				self.handle.sendto(buf, 0, (self.broadcast, self.port))

			def recv(self, n):
				buf, addrinfo = self.handle.recvfrom(n)
				if addrinfo[0] != self.address:
					print("Found peer %s:%d" % addrinfo)

		def broadcaster():
			udp = UDP(PING_PORT_NUMBER)

			poller = zmq.Poller()
			poller.register(udp.handle, zmq.POLLIN)

			# Send first ping right away
			ping_at = time.time()

			while True:
				timeout = ping_at - time.time()
				if timeout < 0:
					timeout = 0
				try:
					events = dict(poller.poll(1000* timeout))
				except KeyboardInterrupt:
					print("interrupted")
					break

				# Someone answered our ping
				if udp.handle.fileno() in events:
					udp.recv(PING_MSG_SIZE)

				if time.time() >= ping_at:
					# Broadcast our beacon
					print ("Pinging peers...")
					udp.send('!')
					ping_at = time.time() + PING_INTERVAL


					
					
					
					
					
					
		import threading
		from random import choice
		class ClientTask(threading.Thread):
			"""ClientTask"""
			def __init__(self):
				threading.Thread.__init__ (self)

			def run(self):
				context = zmq.Context()
				socket = context.socket(zmq.DEALER)
				identity = 'worker-%d' % (choice([0,1,2,3,4,5,6,7,8,9]))
				socket.setsockopt(zmq.IDENTITY, identity )
				socket.connect('tcp://localhost:5570')
				print 'Client %s started' % (identity)
				poll = zmq.Poller()
				poll.register(socket, zmq.POLLIN)
				reqs = 0
				while True:
					for i in xrange(5):
						sockets = dict(poll.poll(1000))
						if socket in sockets:
							if sockets[socket] == zmq.POLLIN:
								msg = socket.recv()
								print 'Client %s received: %s\n' % (identity, msg)
								del msg
					reqs = reqs + 1
					print 'Req #%d sent..' % (reqs)
					socket.send('request #%d' % (reqs))

				socket.close()
				context.term()

		class ServerTask(threading.Thread):
			"""ServerTask"""
			def __init__(self):
				threading.Thread.__init__ (self)

			def run(self):
				context = zmq.Context()
				frontend = context.socket(zmq.ROUTER)
				frontend.bind('tcp://*:5570')

				backend = context.socket(zmq.DEALER)
				backend.bind('inproc://backend')

				workers = []
				for i in xrange(5):
					worker = ServerWorker(context)
					worker.start()
					workers.append(worker)

				poll = zmq.Poller()
				poll.register(frontend, zmq.POLLIN)
				poll.register(backend,  zmq.POLLIN)

				while True:
					sockets = dict(poll.poll())
					if frontend in sockets:
						if sockets[frontend] == zmq.POLLIN:
							_id = frontend.recv()
							msg = frontend.recv()
							print 'Server received %s id %s\n' % (msg, _id)
							backend.send(_id, zmq.SNDMORE)
							backend.send(msg)
					if backend in sockets:
						if sockets[backend] == zmq.POLLIN:
							_id = backend.recv()
							msg = backend.recv()
							print 'Sending to frontend %s id %s\n' % (msg, _id)
							frontend.send(_id, zmq.SNDMORE)
							frontend.send(msg)

				frontend.close()
				backend.close()
				context.term()

		class ServerWorker(threading.Thread):
			"""ServerWorker"""
			def __init__(self, context):
				threading.Thread.__init__ (self)
				self.context = context

			def run(self):
				worker = self.context.socket(zmq.DEALER)
				worker.connect('inproc://backend')
				print 'Worker started'
				while True:
					_id = worker.recv()
					msg = worker.recv()
					print 'Worker received %s from %s' % (msg, _id)
					replies = choice(xrange(5))
					for i in xrange(replies):
						time.sleep(1/choice(range(1,10)))
						worker.send(_id, zmq.SNDMORE)
						worker.send(msg)

					del msg

				worker.close()

		def server_start():
			"""main function
			Here's how it works:

			Clients connect to the server and send requests.
			For each request, the server sends 0 or more replies.
			Clients can send multiple requests without waiting for a reply.
			Servers can send multiple replies without waiting for new requests.

			The example runs in one process, with multiple threads simulating a 
			real multiprocess architecture. When you run the example, you'll 
			see three clients (each with a random ID), printing out the 
			replies they get from the server. Look carefully and you'll see 
			each client task gets 0 or more replies per request.

			Some comments on this code:

			The clients send a request once per second, and get zero or more 
			replies back. To make this work using zmq_poll(), we can't simply 
			poll with a 1-second timeout, or we'd end up sending a new request 
			only one second after we received the last reply. So we poll at a 
			high frequency (100 times at 1/100th of a second per poll), which 
			is approximately accurate.

			The server uses a pool of worker threads, each processing one 
			request synchronously. It connects these to its frontend socket 
			using an internal queue. It connects the frontend and backend 
			sockets using a zmq_proxy() call.
			"""
			server = ServerTask()
			server.start()
			for i in xrange(3):
				client = ClientTask()
				client.start()

			server.join()


			
			
			
			
			
			
			
			
			
		def msreader():
			# encoding: utf-8
			#
			#   Reading from multiple sockets
			#   This version uses a simple recv loop
			#
			#   Author: Jeremy Avnet (brainsik) <spork(dash)zmq(at)theory(dot)org>
			#

			# Prepare our context and sockets
			context = zmq.Context()

			# Connect to task ventilator
			receiver = context.socket(zmq.PULL)
			receiver.connect("tcp://localhost:5557")

			# Connect to weather server
			subscriber = context.socket(zmq.SUB)
			subscriber.connect("tcp://localhost:5556")
			subscriber.setsockopt(zmq.SUBSCRIBE, "10001")

			# Process messages from both sockets
			# We prioritize traffic from the task ventilator
			while True:

				# Process any waiting tasks
				while True:
					try:
						rc = receiver.recv(zmq.DONTWAIT)
					except zmq.ZMQError:
						break
					# process task

				# Process any waiting weather updates
				while True:
					try:
						rc = subscriber.recv(zmq.DONTWAIT)
					except zmq.ZMQError:
						break
					# process weather update

				# No activity, so sleep for 1 msec
				time.sleep(0.001)

		def mspooler():
			# encoding: utf-8
			#
			#   Reading from multiple sockets
			#   This version uses zmq.Poller()
			#
			#   Author: Jeremy Avnet (brainsik) <spork(dash)zmq(at)theory(dot)org>
			#

			# Prepare our context and sockets
			context = zmq.Context()

			# Connect to task ventilator
			receiver = context.socket(zmq.PULL)
			receiver.connect("tcp://localhost:5557")

			# Connect to weather server
			subscriber = context.socket(zmq.SUB)
			subscriber.connect("tcp://localhost:5556")
			subscriber.setsockopt(zmq.SUBSCRIBE, "10001")

			# Initialize poll set
			poller = zmq.Poller()
			poller.register(receiver, zmq.POLLIN)
			poller.register(subscriber, zmq.POLLIN)

			# Process messages from both sockets
			while True:
				socks = dict(poller.poll())

				if receiver in socks and socks[receiver] == zmq.POLLIN:
					message = receiver.recv()
					# process task

				if subscriber in socks and socks[subscriber] == zmq.POLLIN:
					message = subscriber.recv()
					# process weather update
					
		def sink():
			# Task sink
			# Binds PULL socket to tcp://localhost:5558
			# Collects results from workers via that socket
			#
			# Author: Lev Givon <lev(at)columbia(dot)edu>


			context = zmq.Context()

			# Socket to receive messages on
			receiver = context.socket(zmq.PULL)
			receiver.bind("tcp://*:5558")

			# Wait for start of batch
			s = receiver.recv(zmq.DONTWAIT)

			# Start our clock now
			tstart = time.time()

			# Process 100 confirmations
			total_msec = 0
			for task_nbr in range(100):
				s = receiver.recv()
				if task_nbr % 10 == 0:
					sys.stdout.write(':')
				else:
					sys.stdout.write('.')

			# Calculate and report duration of batch
			tend = time.time()
			print "Total elapsed time: %d msec" % ((tend-tstart)*1000)

		def worker():
			# Task worker
			# Connects PULL socket to tcp://localhost:5557
			# Collects workloads from ventilator via that socket
			# Connects PUSH socket to tcp://localhost:5558
			# Sends results to sink via that socket
			#
			# Author: Lev Givon <lev(at)columbia(dot)edu>


			context = zmq.Context()

			# Socket to receive messages on
			receiver = context.socket(zmq.PULL)
			receiver.connect("tcp://localhost:5557")

			# Socket to send messages to
			sender = context.socket(zmq.PUSH)
			sender.connect("tcp://localhost:5558")

			# Process tasks forever
			while True:
				s = receiver.recv(zmq.DONTWAIT)

				# Simple progress indicator for the viewer
				sys.stdout.write('.')
				sys.stdout.flush()

				# Do the work
				time.sleep(int(s)*0.001)

				# Send results to sink
				sender.send('')

				
				
				
				
				
				

		#psutil.get_pid_list()
		# psutil.get_users()
		# [user(name='giampaolo', terminal='pts/2', host='localhost', started=1340737536.0),
		# user(name='giampaolo', terminal='pts/3', host='localhost', started=1340737792.0)]
		#psutil.get_boot_time()
		#used	  = Column(String(50))
		#'sqlite:///foo.db'
		#'sqlite:////absolute/path/to/foo.db'
		#Session.add_all( [] )
		#our_user = session.query(User).filter_by(name='ed').first()
		#session.query(User).filter(User.name.in_(['Edwardo', 'fakeuser'])).all() 
		#for name, fullname in session.query(User.name, User.fullname): 
		#	 print name, fullname
		#for row in session.query(User, User.name).all(): 
		#	 print row.User, row.name
		#for row in session.query(User.name.label('name_label')).all(): 
		#	 print(row.name_label)
		#for u in session.query(User).order_by(User.id)[1:3]: 
		#	 print u
		#session.query(User).filter(User.name.like('%ed')).count()
		#session.query(func.count(User.name), User.name).group_by(User.name).all()
		#for u, a in session.query(User, Address).\
		#			 filter(User.id==Address.user_id).\
		#			 filter(Address.email_address=='jack@google.com').\
		#			 all():	  
		#	 print u, a
		#<User('jack','Jack Bean', 'gjffdd')> <Address('jack@google.com')>
		#session.query(User).\
		#		 join(Address).\
		#		 filter(Address.email_address=='jack@google.com').\
		#		 all() 
		#for u, count in session.query(User, stmt.c.address_count).\
		#	  outerjoin(stmt, User.id==stmt.c.user_id).order_by(User.id): 
		#	  print u, count
		#<User('ed','Ed Jones', 'f8s7ccs')> None
		#session.dirty # prints changes to be made


