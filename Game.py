# Libraries
from direct.showbase.ShowBase import ShowBase
from panda3d.core import CollisionTraverser, CollisionNode
from panda3d.core import CollisionHandlerQueue, CollisionSphere
from panda3d.core import Filename, AmbientLight, DirectionalLight
from panda3d.core import PandaNode, NodePath, Camera, TextNode
from panda3d.core import CollideMask, BitMask32
from direct.gui.OnscreenText import OnscreenText
from direct.actor.Actor import Actor
import random
import sys
import os
import math
import winsound

def addInstructions(pos, msg):
    return OnscreenText(text=msg, style=1, fg=(0.9, 0, 0, 1), scale=.05,
                        shadow=(0.5, 0.5, 0.5, 1), parent=base.a2dTopLeft,
                        pos=(0.08, -pos - 0.04), align=TextNode.ALeft)

def addTitle(text):
    return OnscreenText(text=text, style=1, fg=(0, 0, 0.9, 1), scale=.07,
                        parent=base.a2dBottomRight, align=TextNode.ARight,
                        pos=(-0.1, 0.09), shadow=(0, 0, 0, 1))


class Project(ShowBase):
    def __init__(self):

        ShowBase.__init__(self)
        self.win.setClearColor((0.455, 0.816, 0.945, 1))

        self.keyMap = {
            "left": 0, "right": 0, "forward": 0, "backward": 0, "jump": 0, "action": 0}


        # Mise en place des instructions
        self.title = addTitle(
            "Project : 'Escape the forest'")
        self.inst1 = addInstructions(0.06, "[ECHAP]: Quit")
        self.inst2 = addInstructions(0.12, "[Left arrow]: Turn Freddy left")
        self.inst3 = addInstructions(0.18, "[Right arrow]: Turn Freddy right")
        self.inst4 = addInstructions(0.24, "[Top arrow]: Make Freddy move forward")
        self.inst5 = addInstructions(0.30, "Bottom arrow]: Make Freddy move back")
        self.inst6 = addInstructions(0.36, "[Space]: Make Freddy jump")

        # 3D objects
        self.map = loader.loadModel("obj/Map.egg.pz")
        self.map.reparentTo(render)

        self.walls = loader.loadModel("obj/Wall.egg")
        self.walls.reparentTo(render)

        self.bridge = Actor("obj/Bridge.egg",
		                  {"Drop" : "obj/Bridge.egg"})
        self.bridge.reparentTo(render)
        self.bridge.pose("Drop", 0)

        self.lever = Actor("obj/Lever.egg",
                            {"OnOff" : "obj/Lever.egg"})
        self.lever.reparentTo(render)
        self.lever.setPos(0, 12, 1)
        self.lever.pose("OnOff", 0)

        self.lever1 = Actor("obj/Lever.egg",
		                      {"OnOff" : "obj/Lever.egg"})
        self.lever1.reparentTo(render)
        self.lever1.setPos(50, 16, 1)
        self.lever1.pose("OnOff", 0)

        self.lever2 = Actor("obj/Lever.egg",
		                      {"OnOff" : "obj/Lever.egg"})
        self.lever2.reparentTo(render)
        self.lever2.setPos(22, 92, 1)
        self.lever2.pose("OnOff", 0)

        self.dirt = Actor("obj/Dirt.egg",
                            {"Up" : "obj/Dirt.egg"})
        self.dirt.reparentTo(render)

        self.stone = Actor("obj/Stone.egg",
                            {"Fall" : "obj/Stone.egg"})
        self.stone.reparentTo(render)

        # Creation of the main character, Freddy
        FreddyStartPos = (8,-8,1)
        self.Freddy = Actor("obj/Freddy.egg" ,
                            {"Run" : "obj/Run.egg",
							 "Pose" : "obj/Pose.egg"})
        self.Freddy.reparentTo(render)
        self.Freddy.setScale(1.4)
        self.Freddy.setPos(FreddyStartPos)
        self.Freddy.setH(180)

        winsound.PlaySound("sound/music.wav", winsound.SND_ASYNC)

        self.floater = NodePath(PandaNode("floater"))
        self.floater.reparentTo(self.Freddy)
        self.floater.setZ(1)

        # Controls for move and interact

        self.accept("escape", sys.exit)
        self.accept("arrow_left", self.setKey, ["left", True])
        self.accept("arrow_right", self.setKey, ["right", True])
        self.accept("arrow_up", self.setKey, ["forward",True])
        self.accept("arrow_down", self.setKey, ["backward", True])
        self.accept( "space" , self.setKey,["jump",True])
        self.accept( "a" , self.setKey,["action",True])

        self.accept("arrow_left-up", self.setKey, ["left", False])
        self.accept("arrow_right-up", self.setKey, ["right", False])
        self.accept("arrow_up-up", self.setKey, ["forward", False])
        self.accept("arrow_down-up", self.setKey, ["backward", False])
        self.accept( "space-up" , self.setKey,["jump",False])
        self.accept( "a-up" , self.setKey,["action",False])

        taskMgr.add(self.movement, "Movement")

        self.moving = False

        self.disableMouse()

        ambientLight = AmbientLight("ambientLight")
        ambientLight.setColor((1, 1, 1, 1))
        render.setLight(render.attachNewNode(ambientLight))

        # Collisions
        self.cTrav = CollisionTraverser()
        self.FreddyGroundHandler = CollisionHandlerQueue()
        self.FreddyGroundSphere = CollisionSphere(0,0,0.5,0.3) #Coordinates of the center and radius
        self.FreddyGroundCol = CollisionNode('freddySphere')
        self.FreddyGroundCol.addSolid(self.FreddyGroundSphere)
        self.FreddyGroundCol.setFromCollideMask(BitMask32.bit(0))
        self.FreddyGroundCol.setIntoCollideMask(BitMask32.allOff())
        self.FreddyGroundColNp = self.Freddy.attachNewNode(self.FreddyGroundCol)
        self.cTrav.addCollider(self.FreddyGroundColNp, self.FreddyGroundHandler)

    def setKey(self, key, value) :
        self.keyMap[key] = value

    def movement(self, task):
        dt = globalClock.getDt()
        startpos = self.Freddy.getPos()

        speed = -5

        if self.keyMap["left"] :
            self.Freddy.setH(-90)
            self.Freddy.setY(self.Freddy, speed * dt)
        if self.keyMap["right"] :
            self.Freddy.setH(90)
            self.Freddy.setY(self.Freddy, speed * dt)
        if self.keyMap["forward"] :
            self.Freddy.setH(180)
            self.Freddy.setY(self.Freddy, speed * dt)
        if self.keyMap["backward"] :
            self.Freddy.setH(0)
            self.Freddy.setY(self.Freddy, speed * dt)

        relative_speed = 5*math.sqrt(2)-5
        if self.keyMap["left"] and self.keyMap["forward"] :
            self.Freddy.setH(-135)
            self.Freddy.setY(self.Freddy, relative_speed *dt)

        if self.keyMap["left"] and self.keyMap["backward"] :
            self.Freddy.setH(-45)
            self.Freddy.setY(self.Freddy, relative_speed *dt)

        if self.keyMap["right"] and self.keyMap["forward"] :
            self.Freddy.setH(135)
            self.Freddy.setY(self.Freddy, relative_speed *dt)

        if self.keyMap["right"] and self.keyMap["backward"] :
            self.Freddy.setH(45)
            self.Freddy.setY(self.Freddy, relative_speed *dt)

        deltax = self.lever.getX() - self.Freddy.getX()
        deltay = self.lever.getY() - self.Freddy.getY()
        deltaz = self.lever.getZ() - self.Freddy.getZ()

        deltax1 = self.lever1.getX() - self.Freddy.getX()
        deltay1 = self.lever1.getY() - self.Freddy.getY()
        deltaz1 = self.lever1.getZ() - self.Freddy.getZ()

        deltax2 = self.lever2.getX() - self.Freddy.getX()
        deltay2 = self.lever2.getY() - self.Freddy.getY()
        deltaz2 = self.lever2.getZ() - self.Freddy.getZ()

        delta = math.sqrt(deltax**2 + deltay**2 + deltaz**2)
        delta1 = math.sqrt(deltax1**2 + deltay1**2 + deltaz1**2)
        delta2 = math.sqrt(deltax2**2 + deltay2**2 + deltaz2**2)

        if delta < 3 and self.keyMap["action"] :
            self.lever.play("OnOff")
            self.bridge.play("Drop")

        if delta1 < 3 and self.keyMap["action"] :
            self.lever1.play("OnOff")
            self.stone.play("Fall")

        if delta2 < 30 and self.keyMap["action"] :
            self.lever2.play("OnOff")
            self.dirt.play("Up")

        if self.keyMap["forward"] or self.keyMap["left"] or self.keyMap["right"] or self.keyMap["backward"] :
            if self.moving is False :
                self.Freddy.loop("Run")
                self.moving = True
        else :
            if self.moving :
                self.Freddy.stop()
                self.Freddy.loop("Pose")
                self.moving = False

        if self.Freddy.getZ() < 1 :
            self.Freddy.setZ(1)
        dt = globalClock.getDt()
        maxZ = 5
        if self.keyMap["jump"] == True and self.Freddy.getZ() <= maxZ:
            self.Freddy.setZ(self.Freddy.getZ() + 5 *dt)
        if self.keyMap["jump"] == False and self.Freddy.getZ() >= 1:
            self.Freddy.setZ(self.Freddy, -2 *dt)

        # Collisions again
        self.cTrav.traverse(render)
        entries = []
        for i in range(self.FreddyGroundHandler.getNumEntries()):
            entry = self.FreddyGroundHandler.getEntry(i)
            entries.append(entry)
        if (len(entries)>0) and (entries[0].getIntoNode().getName() == "Htbox"):
            self.Freddy.setPos(startpos)

        camx = self.Freddy.getX() - self.camera.getX()
        if camx > 8.625 or camx < 8.625 :
            self.camera.setX(self.Freddy.getX() + 8.625)

        camy = self.Freddy.getY() - self.camera.getY()
        if camy > -18.375 or camy < -18.375 :
            self.camera.setY(self.Freddy.getY() - 18.375)

        camz = self.Freddy.getZ() - self.Freddy.getZ()
        if camz > 13.125 or camz < 13.125 :
            self.camera.setZ(self.Freddy.getZ() + 13.125)

        self.camera.lookAt(self.floater)

        return task.cont

# Launch the game
demo = Project()
demo.run()
