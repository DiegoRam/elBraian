#imports
import os.path
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.websocket
import ConfigParser, os
from tornado.options import define,options
from tornado import template, websocket
from pyjade.ext.tornado import patch_tornado
from braianDriver.robot import Robot
import logging
import json
from utils.poolsockets import PoolWebSocketHandler
from time import sleep

config = ConfigParser.ConfigParser()
config.read('config/application.cfg')
env = config.get("system","env")

patch_tornado()
define("port", default=80, help="run on the given port",type=int)
log = logging.getLogger("webserver")
log.setLevel(logging.DEBUG)

sockets =  PoolWebSocketHandler()

class IndexHandler(tornado.web.RequestHandler):
	def get(self):
		pic_url = "http://elbraian.bot:8095/?action=stream" if (env=="prod") else "/static/img/bg-video.png"
		self.render('index.jade', pic_url=pic_url)
		
class RobotHandler(tornado.websocket.WebSocketHandler):
	ROBOT = Robot()
	"""
	this class represent the basic socket operation to move the wheels
	"""

	def executeStep(self, heading, time_hold):
			
			if (heading == "FORWARD"):
				self.ROBOT.set_forward()
				self.ROBOT.move(speed=Robot.SPEED_MEDIUM)
			elif (heading == "BACKWARD"):
				self.ROBOT.set_backward()
				self.ROBOT.move(speed=Robot.SPEED_HIGH)
			elif (heading == "ROTATE-LEFT"):
				self.ROBOT.set_rotate_left()
				self.ROBOT.move(speed=Robot.SPEED_LOW)
			elif (heading == "ROTATE-RIGHT"):
				self.ROBOT.set_rotate_right()
				self.ROBOT.move(speed=Robot.SPEED_LOW)
			elif (heading == "FORWARD-TURNING-LEFT"):
				self.ROBOT.set_forward()
				self.ROBOT.move(arc=Robot.LEFT_ARC_CLOSE)
			elif (heading == "FORWARD-TURNING-RIGHT"):
				self.ROBOT.set_forward()
				self.ROBOT.move(arc=Robot.RIGHT_ARC_CLOSE)
			elif (heading == "BACKWARD-TURNING-LEFT"):
				self.ROBOT.set_backward()
				self.ROBOT.move(arc=Robot.LEFT_ARC_CLOSE)
			elif (heading == "BACKWARD-TURNING-RIGHT"):
				self.ROBOT.set_backward()
				self.ROBOT.move(arc=Robot.RIGHT_ARC_CLOSE)


			if time_hold > 0:
				sleep(time_hold/1000);
				self.ROBOT.stop()



	def open(self):
		sockets.clients.append(self)
		log.debug("client connected..")
		message = {}
		message["message"] = "INFO"
		message["payload"] = {}
		message["payload"]["client_count"] = sockets.count()
		sockets.broadcast(json.dumps(message))
		
	def on_close(self):
		sockets.clients.remove(self)
		message = {}
		message["message"] = "INFO"
		message["payload"] = {}
		message["payload"]["client_count"] = sockets.count()
		log.debug("get the hell out of here!")

	def on_message(self,message):
		log.debug(message)
		message_obj = json.loads(message)

		if "payload" in message_obj:
			heading = message_obj["payload"].get("heading","")
			hold_time = message_obj["payload"].get("hold",0)
		
		message_response = {"message": "INFO"}
		message_response["payload"] = {} 

		if message_obj["message"] == "MOVE":
			self.executeStep(heading, time_hold = 0)

		elif message_obj["message"] == "SEQUENCE":

			message_response["payload"]["status"] = "BLOCKED"
			count = len(message_obj["payload"]["steps"])
			message_response["payload"]["steps"] = count
			message_response["payload"]["client_count"] = str(sockets.count())
			#TODO please refactor this crap
			sockets.broadcast_less(self,json.dumps(message_response))
			message_response["payload"]["status"] = "RUNNING"
			self.write_message(json.dumps(message_response))
			for step in message_obj["payload"]["steps"]:
				log.debug("execute step: " + str(step["id"]))
				self.executeStep(step["heading"], step["hold"])
				message_response["payload"]["remaining"] = count - (step["id"] + 1)
				sockets.broadcast(json.dumps(message_response))
			log.debug("ending sequence")
			message_response["payload"]["status"] = "AVAILABLE"
			sockets.broadcast(json.dumps(message_response))

		elif (message_obj["message"] == "STOP"):
				self.ROBOT.stop()

		elif message_obj["message"] == "HEAD-RIGHT":
			self.ROBOT.head_move_right()
		elif message_obj["message"] == "HEAD-LEFT":
			self.ROBOT.head_move_left()
		elif message_obj["message"] == "HEAD-UP":
			self.ROBOT.head_move_up()
		elif message_obj["message"] == "HEAD-DOWN":
			self.ROBOT.head_move_down()
	

	def create_message(self, action):
		pass


class CameraHandler(tornado.websocket.WebSocketHandler):
	def open(self):
		self.write_message("connected to de camera")

	def start_transmitVideo(self):
		pass

class ConsoleHandler(tornado.web.RequestHandler):
	def get(self):
		self.render('console.jade', code='')
	def post(self):
		code = json.loads(self.request.body)
		exec(code["code"])
		self.set_status(200)
		self.finish()

class NewConsole(tornado.web.RequestHandler):
	def get(self):
		self.render('new_console.jade')

if __name__ == '__main__':
	tornado.options.parse_command_line()
	app = tornado.web.Application(
		handlers=[
			(r"/",IndexHandler),
			(r"/favicon.ico", tornado.web.StaticFileHandler,{'path':'static'}),
			(r"/robot",RobotHandler),
			(r"/console",ConsoleHandler),
			(r"/newconsole",NewConsole)
		],
		template_path=os.path.join(os.path.dirname(__file__),"templates"),
		static_path=os.path.join(os.path.dirname(__file__),"static"),
		debug=True	
	)
	http_server = tornado.httpserver.HTTPServer(app)
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()