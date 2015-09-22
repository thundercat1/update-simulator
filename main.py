from __future__ import print_function
import time

class SkuProcessor:
	def __init__(self):
		self.pull_interval = None
		self.pull_amount = None
		self.upstream_storage = None
		self.downstream_storage = None
		self.speed = 1
		self.next_pull = 0


	def run(self, t):
		if t >= self.next_pull:
			amount_to_process = min(self.upstream_storage.stored, self.pull_amount)

			self.print_action(amount_to_process)

			self.upstream_storage.remove_skus(amount_to_process)
			self.downstream_storage.add_skus(amount_to_process)
			self.next_pull = t + self.pull_interval

	def print_action(self, amount_to_process):
		print(self.name, ' processing ', amount_to_process, ' skus.')

	def print_upstream_storage_status(self):
		print(self.upstream_storage.name, ':\t', self.upstream_storage.stored)


class SkuStorage:
	def __init__(self):
		self.stored = 0

	def add_skus(self, n):
		self.stored += n

	def remove_skus(self, n):
		self.stored -= n

class Simulation:
	def __init__(self, processors):
		self.processors = processors
	
	def set_speed(self, speed):
		self.speed = speed
		for processor in processors:
			processor.speed = speed

	def add_skus(self, n):
		self.starting_storage.add_skus(n)

	def run(self):
		#run for n seconds
		t = 0

		while self.ending_storage.stored < 1000:
			for processor in processors:
				processor.run(t)

			for processor in processors:
				processor.print_upstream_storage_status()

			t += 1

			print('\r')


if __name__ == '__main__':
	processors = []

	mat_mongo = SkuStorage()
	mat_mongo.name = 'MAT Mongo'

	hub_batch = SkuStorage()
	hub_batch.name = 'Hub Batch'

	atg_feed = SkuStorage()
	atg_feed.name = 'ATG Feed'

	atg = SkuStorage()
	atg.name = 'ATG'

	product_update_queue = SkuStorage()
	product_update_queue.name = 'Product API'

	site = SkuStorage()
	site.name = 'Live to customer'


	mat = SkuProcessor()
	processors.append(mat)
	mat.name = 'MAT'
	mat.upstream_storage = mat_mongo
	mat.downstream_storage = hub_batch
	mat.pull_interval = 1
	mat.pull_amount = 50

	hub = SkuProcessor()
	processors.append(hub)
	hub.name = 'Hub'
	hub.upstream_storage = hub_batch
	hub.downstream_storage = atg_feed
	hub.pull_interval = 10*60
	hub.pull_amount = float('inf')

	listener = SkuProcessor()
	processors.append(listener)
	listener.name = 'ATG Hub Listener'
	listener.upstream_storage = atg_feed
	listener.downstream_storage = product_update_queue
	listener.pull_interval = 1
	listener.pull_amount = 100

	product_updater = SkuProcessor()
	processors.append(product_updater)
	product_updater.name = 'Product API Consumer'
	product_updater.upstream_storage = product_update_queue
	product_updater.downstream_storage = site
	product_updater.pull_interval = 1
	product_updater.pull_amount = 5


	sim = Simulation(processors)
	sim.starting_storage = mat_mongo
	sim.ending_storage = site
	sim.add_skus(10000)
	sim.run()