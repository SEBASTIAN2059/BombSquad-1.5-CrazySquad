import weakref
import random
import bs
import bsUtils
import bsInternal
import bsGame
import bsMap
import settings

# list of defined spazzes
appearances = {}


def getAppearances(includeLocked=False):
	#import bsInternal
    import bsAchievement
    disallowed = []
    if not includeLocked:
        # hmm yeah this'll be tough to hack...
        if not bsInternal._getPurchased('characters.santa'):
            disallowed.append('Santa Claus')
        if not bsInternal._getPurchased('characters.frosty'):
            disallowed.append('Frosty')
        if not bsInternal._getPurchased('characters.bones'):
            disallowed.append('Bones')
        if not bsInternal._getPurchased('characters.bernard'):
            disallowed.append('Bernard')
        if not bsInternal._getPurchased('characters.pixie'):
            disallowed.append('Pixel')
        if not bsInternal._getPurchased('characters.pascal'):
            disallowed.append('Pascal')
        if not bsInternal._getPurchased('characters.actionhero'):
            disallowed.append('Todd McBurton')
        if not bsInternal._getPurchased('characters.taobaomascot'):
            disallowed.append('Taobao Mascot')
        if not bsInternal._getPurchased('characters.agent'):
            disallowed.append('Agent Johnson')
        if not bsInternal._getPurchased('characters.jumpsuit'):
            disallowed.append('Lee')
        if not bsInternal._getPurchased('characters.assassin'):
            disallowed.append('Zola')
        if not bsInternal._getPurchased('characters.wizard'):
            disallowed.append('Grumbledorf')
        if not bsInternal._getPurchased('characters.cowboy'):
            disallowed.append('Butch')
        if not bsInternal._getPurchased('characters.witch'):
            disallowed.append('Witch')
        if not bsInternal._getPurchased('characters.warrior'):
            disallowed.append('Warrior')
        if not bsInternal._getPurchased('characters.superhero'):
            disallowed.append('Middle-Man')
        if not bsInternal._getPurchased('characters.alien'):
            disallowed.append('Alien')
        if not bsInternal._getPurchased('characters.oldlady'):
            disallowed.append('OldLady')
        if not bsInternal._getPurchased('characters.gladiator'):
            disallowed.append('Gladiator')
        if not bsInternal._getPurchased('characters.wrestler'):
            disallowed.append('Wrestler')
        if not bsInternal._getPurchased('characters.operasinger'):
            disallowed.append('Gretel')
        if not bsInternal._getPurchased('characters.robot'):
            disallowed.append('Robot')
        if not bsInternal._getPurchased('characters.cyborg'):
            disallowed.append('B-9000')
        if not bsInternal._getPurchased('characters.bunny'):
            disallowed.append('Easter Bunny')
        if not bsInternal._getPurchased('characters.kronk'):
            disallowed.append('Kronk')
        if not bsInternal._getPurchased('characters.zoe'):
            disallowed.append('Zoe')
        if not bsInternal._getPurchased('characters.jackmorgan'):
            disallowed.append('Jack Morgan')
        if not bsInternal._getPurchased('characters.mel'):
            disallowed.append('Mel')
        if not bsInternal._getPurchased('characters.snakeshadow'):
            disallowed.append('Snake Shadow')
            
        import bsAchievement
        a = bsAchievement.getAchievement('Blanco o Negro')
        if not a.isComplete(): disallowed.append('Panda')
        b = bsAchievement.getAchievement('Mega Bomber')
        if not b.isComplete(): disallowed.append('SEBASTIAN2059')
        c = bsAchievement.getAchievement('Derrota Monstruosa')
        if not c.isComplete(): disallowed.append('Mostro')
        d = bsAchievement.getAchievement('Massacrer')
        if not d.isComplete(): disallowed.append('Oso Espectro')
        
    return [s for s in appearances.keys() if s not in disallowed]


gPowerupWearOffTime = 20000
gBasePunchPowerScale = 1.2 # obsolete - just used for demo guy now
gBasePunchCooldown = 400
gLameBotColor = (1.2, 0.9, 0.2)
gLameBotHighlight = (1.0, 0.5, 0.6)
gDefaultBotColor = (0.6, 0.6, 0.6)
gDefaultBotHighlight = (0.1, 0.3, 0.1)
gProBotColor = (1.0, 0.2, 0.1)
gProBotHighlight = (0.6, 0.1, 0.05)
gLastTurboSpamWarningTime = -99999


class _PickupMessage(object):
    'We wanna pick something up'
    pass


class _PunchHitMessage(object):
    'Message saying an object was hit'
    pass


class _CurseExplodeMessage(object):
    'We are cursed and should blow up now.'
    pass


class _BombDiedMessage(object):
    "A bomb has died and thus can be recycled"
    pass


class Appearance(object):
    """Create and fill out one of these suckers to define a spaz appearance"""
    def __init__(self, name):
        self.name = name
        if appearances.has_key(self.name):
            raise Exception("spaz appearance name \""
                            + self.name + "\" already exists.")
        appearances[self.name] = self
        self.colorTexture = ""
        self.headModel = ""
        self.torsoModel = ""
        self.pelvisModel = ""
        self.upperArmModel = ""
        self.foreArmModel = ""
        self.handModel = ""
        self.upperLegModel = ""
        self.lowerLegModel = ""
        self.toesModel = ""
        self.jumpSounds = []
        self.attackSounds = []
        self.impactSounds = []
        self.deathSounds = []
        self.pickupSounds = []
        self.fallSounds = []
        self.style = 'spaz'
        self.defaultColor = None
        self.defaultHighlight = None


class SpazFactory(object):
    """
    Category: Game Flow Classes

    Wraps up media and other resources used by bs.Spaz instances.
    Generally one of these is created per bs.Activity and shared
    between all spaz instances.  Use bs.Spaz.getFactory() to return
    the shared factory for the current activity.

    Attributes:

       impactSoundsMedium
          A tuple of bs.Sounds for when a bs.Spaz hits something kinda hard.

       impactSoundsHard
          A tuple of bs.Sounds for when a bs.Spaz hits something really hard.

       impactSoundsHarder
          A tuple of bs.Sounds for when a bs.Spaz hits something really
          really hard.

       singlePlayerDeathSound
          The sound that plays for an 'importan' spaz death such as in
          co-op games.

       punchSound
          A standard punch bs.Sound.
       
       punchSoundsStrong
          A tuple of stronger sounding punch bs.Sounds.

       punchSoundStronger
          A really really strong sounding punch bs.Sound.

       swishSound
          A punch swish bs.Sound.

       blockSound
          A bs.Sound for when an attack is blocked by invincibility.

       shatterSound
          A bs.Sound for when a frozen bs.Spaz shatters.

       splatterSound
          A bs.Sound for when a bs.Spaz blows up via curse.

       spazMaterial
          A bs.Material applied to all of parts of a bs.Spaz.

       rollerMaterial
          A bs.Material applied to the invisible roller ball body that a bs.Spaz
          uses for locomotion.
    
       punchMaterial
          A bs.Material applied to the 'fist' of a bs.Spaz.

       pickupMaterial
          A bs.Material applied to the 'grabber' body of a bs.Spaz.

       curseMaterial
          A bs.Material applied to a cursed bs.Spaz that triggers an explosion.
    """

    def _preload(self, character):
        """
        Preload media that will be needed for a given character.
        """
        self._getMedia(character)

    def __init__(self):
        """
        Instantiate a factory object.
        """

        self.impactSoundsMedium = (bs.getSound('impactMedium'),
                                bs.getSound('impactMedium2'))
        self.impactSoundsHard = (bs.getSound('impactHard'),
                                 bs.getSound('impactHard2'),
                                 bs.getSound('impactHard3'))
        self.impactSoundsHarder = (bs.getSound('bigImpact'),
                                   bs.getSound('bigImpact2'))
        self.singlePlayerDeathSound = bs.getSound('playerDeath')
        self.punchSound = bs.getSound('punch01')
        
        self.punchSoundsStrong = (bs.getSound('punchStrong01'),
                                  bs.getSound('punchStrong02'))
        
        self.punchSoundStronger = bs.getSound('superPunch')
        
        self.swishSound = bs.getSound('punchSwish')
        self.blockSound = bs.getSound('block')
        self.shatterSound = bs.getSound('shatter')
        self.splatterSound = bs.getSound('splatter')
        
        self.spazMaterial = bs.Material()
        self.rollerMaterial = bs.Material()
        self.punchMaterial = bs.Material()
        self.pickupMaterial = bs.Material()
        self.curseMaterial = bs.Material()

        footingMaterial = bs.getSharedObject('footingMaterial')
        objectMaterial = bs.getSharedObject('objectMaterial')
        playerMaterial = bs.getSharedObject('playerMaterial')
        regionMaterial = bs.getSharedObject('regionMaterial')
        
        # send footing messages to spazzes so they know when they're on solid
        # ground.
        # eww this should really just be built into the spaz node
        self.rollerMaterial.addActions(
            conditions=('theyHaveMaterial', footingMaterial),
            actions=(('message', 'ourNode', 'atConnect', 'footing', 1),
                     ('message', 'ourNode', 'atDisconnect', 'footing', -1)))

        self.spazMaterial.addActions(
            conditions=('theyHaveMaterial', footingMaterial),
            actions=(('message', 'ourNode', 'atConnect', 'footing', 1),
                     ('message', 'ourNode', 'atDisconnect', 'footing', -1)))
        # punches
        self.punchMaterial.addActions(
            conditions=('theyAreDifferentNodeThanUs',),
            actions=(('modifyPartCollision', 'collide', True),
                     ('modifyPartCollision', 'physical', False),
                     ('message', 'ourNode', 'atConnect', _PunchHitMessage())))
        # pickups
        self.pickupMaterial.addActions(
            conditions=(('theyAreDifferentNodeThanUs',),
                        'and', ('theyHaveMaterial', objectMaterial)),
            actions=(('modifyPartCollision', 'collide', True),
                     ('modifyPartCollision', 'physical', False),
                     ('message', 'ourNode', 'atConnect', _PickupMessage())))
        # curse
        self.curseMaterial.addActions(
            conditions=(('theyAreDifferentNodeThanUs',),
                        'and', ('theyHaveMaterial', playerMaterial)),
            actions=('message', 'ourNode', 'atConnect', _CurseExplodeMessage()))

        self.footImpactSounds = (bs.getSound('footImpact01'),
                                 bs.getSound('footImpact02'),
                                 bs.getSound('footImpact03'))

        self.footSkidSound = bs.getSound('skid01')
        self.footRollSound = bs.getSound('scamper01')

        self.rollerMaterial.addActions(
            conditions=('theyHaveMaterial', footingMaterial),
            actions=(('impactSound', self.footImpactSounds, 1, 0.2),
                     ('skidSound', self.footSkidSound, 20, 0.3),
                     ('rollSound', self.footRollSound, 20, 3.0)))

        self.skidSound = bs.getSound('gravelSkid')

        self.spazMaterial.addActions(
            conditions=('theyHaveMaterial', footingMaterial),
            actions=(('impactSound', self.footImpactSounds, 20, 6),
                     ('skidSound', self.skidSound, 2.0, 1),
                     ('rollSound', self.skidSound, 2.0, 1)))

        self.shieldUpSound = bs.getSound('shieldUp')
        self.shieldDownSound = bs.getSound('shieldDown')
        self.shieldHitSound = bs.getSound('shieldHit')

        # we dont want to collide with stuff we're initially overlapping
        # (unless its marked with a special region material)
        self.spazMaterial.addActions(
            conditions=((('weAreYoungerThan', 51),
                         'and', ('theyAreDifferentNodeThanUs',)),
                        'and', ('theyDontHaveMaterial', regionMaterial)),
            actions=(('modifyNodeCollision', 'collide', False)))
        
        self.spazMedia = {}

        # lets load some basic rules (allows them to be tweaked from the
        # master server)
        self.shieldDecayRate = bsInternal._getAccountMiscReadVal('rsdr', 10.0)
        self.punchCooldown = bsInternal._getAccountMiscReadVal('rpc', 400)
        self.punchCooldownGloves = \
            bsInternal._getAccountMiscReadVal('rpcg', 300)
        self.punchPowerScale = bsInternal._getAccountMiscReadVal('rpp', 1.2)
        self.punchPowerScaleGloves = \
            bsInternal._getAccountMiscReadVal('rppg', 1.4)
        self.maxShieldSpilloverDamage = \
            bsInternal._getAccountMiscReadVal('rsms', 500)

    def _getStyle(self, character):
        return appearances[character].style
        
    def _getMedia(self, character):
        t = appearances[character]
        if not self.spazMedia.has_key(character):
            m = self.spazMedia[character] = {
                'jumpSounds':[bs.getSound(s) for s in t.jumpSounds],
                'attackSounds':[bs.getSound(s) for s in t.attackSounds],
                'impactSounds':[bs.getSound(s) for s in t.impactSounds],
                'deathSounds':[bs.getSound(s) for s in t.deathSounds],
                'pickupSounds':[bs.getSound(s) for s in t.pickupSounds],
                'fallSounds':[bs.getSound(s) for s in t.fallSounds],
                'colorTexture':bs.getTexture(t.colorTexture),
                'colorMaskTexture':bs.getTexture(t.colorMaskTexture),
                'headModel':bs.getModel(t.headModel),
                'torsoModel':bs.getModel(t.torsoModel),
                'pelvisModel':bs.getModel(t.pelvisModel),
                'upperArmModel':bs.getModel(t.upperArmModel),
                'foreArmModel':bs.getModel(t.foreArmModel),
                'handModel':bs.getModel(t.handModel),
                'upperLegModel':bs.getModel(t.upperLegModel),
                'lowerLegModel':bs.getModel(t.lowerLegModel),
                'toesModel':bs.getModel(t.toesModel)
            }
        else:
            m = self.spazMedia[character]
        return m
        
class BlackHole(bs.Actor):
    def __init__(self,position = (0,1,0),autoExpand = True,scale = 1,doNotRandomize = False,infinity = False,owner = None):
        bs.Actor.__init__(self)
        self.shields = []
        
        self.position = (position[0]-2+random.random()*4,position[1]+random.random()*2,position[2]-2+random.random()*4) if not doNotRandomize else position
        self.scale = scale
        self.suckObjects = []
        
        self.owner = owner
        
        self.blackHoleMaterial = bs.Material()
        self.suckMaterial = bs.Material()
        self.blackHoleMaterial.addActions(conditions=(('theyDontHaveMaterial', bs.getSharedObject('objectMaterial')),'and',('theyHaveMaterial', bs.getSharedObject('playerMaterial'))),actions=(("modifyPartCollision","collide",True),
                                                      ("modifyPartCollision","physical",False),
                                                      ("call","atConnect", self.touchedSpaz)))
                                                      
        self.blackHoleMaterial.addActions(conditions=(('theyDontHaveMaterial', bs.getSharedObject('playerMaterial')),'and',('theyHaveMaterial', bs.getSharedObject('objectMaterial'))),actions=(("modifyPartCollision","collide",True),
                                                      ("modifyPartCollision","physical",False),
                                                      ("call","atConnect", self.touchedObj)))
                                                  
        self.suckMaterial.addActions(conditions=(('theyHaveMaterial', bs.getSharedObject('objectMaterial'))),actions=(("modifyPartCollision","collide",True),
                                                      ("modifyPartCollision","physical",False),
                                                      ("call","atConnect", self.touchedObjSuck)))
                                                  
                                                  
        self.node = bs.newNode('region',
                       attrs={'position':(self.position[0],self.position[1],self.position[2]),
                              'scale':(scale,scale,scale),
                              'type':'sphere',
                              'materials':[self.blackHoleMaterial]})
                              
        self.suckRadius = bs.newNode('region',
                       attrs={'position':(self.position[0],self.position[1],self.position[2]),
                              'scale':(scale,scale,scale),
                              'type':'sphere',
                              'materials':[self.suckMaterial]})
                              
        def dist():
            bs.emitBGDynamics(position=self.position,emitType='distortion',spread=6,count = 100)
            if self.node.exists():
                bs.gameTimer(1000,dist)
                
        dist()
        
        if not infinity:
            self._dieTimer = bs.Timer(25000,bs.WeakCall(self.explode))
        bsUtils.animateArray(self.node,"scale",3,{0:(0,0,0),300:(self.scale,self.scale,self.scale)},True)
        bsUtils.animateArray(self.suckRadius,"scale",3,{0:(0,0,0),300:(self.scale*8,self.scale*8,self.scale*8)},True)
        
        for i in range(20):
            self.shields.append(bs.newNode('shield',attrs={'color':(random.random(),random.random(),random.random()),'radius':self.scale*2,'position':self.position}))
        def sound():   
            bs.playSound(bs.getSound('blackHole'))
        sound()
        if infinity:
            self.sound2 = bs.Timer(25000,bs.Call(sound),repeat = infinity)
        

    def addMass(self):
        self.scale += 0.15
        self.node.scale = (self.scale,self.scale,self.scale)
        for i in range(2):
            self.shields.append(bs.newNode('shield',attrs={'color':(random.random(),random.random(),random.random()),'radius':self.scale+0.15,'position':self.position}))
            
    def explode(self):
        bs.emitBGDynamics(position=self.position,count=500,scale=1,spread=1.5,chunkType='spark')
        for i in self.shields: bsUtils.animate(i,"radius",{0:0,200:i.radius*5})
        bs.Blast(position = self.position,blastRadius = 10).autoRetain()
        for i in self.shields: i.delete()
        self.node.delete()
        self.suckRadius.delete()
        self.node.handleMessage(bs.DieMessage())
        self.suckRadius.handleMessage(bs.DieMessage())
        

    def touchedSpaz(self):
        node = bs.getCollisionInfo('opposingNode')
        bs.Blast(position = node.position,blastType = 'turret').autoRetain()
        if node.exists():
            if self.owner.exists():
                node.handleMessage(bs.HitMessage(magnitude=1000.0,sourcePlayer = self.owner.getDelegate().getPlayer()))
                try:
                    node.handleMessage(bs.DieMessage())
                except:
                    pass
                bs.shakeCamera(2)
            else:
                node.handleMessage(bs.DieMessage())
        self.addMass()
        
    def touchedObj(self):
        node = bs.getCollisionInfo('opposingNode')
        bs.Blast(position = node.position,blastType = 'turret').autoRetain()
        if node.exists():
            node.handleMessage(bs.DieMessage())
            
            
        
    def touchedObjSuck(self):
        node = bs.getCollisionInfo('opposingNode')
        if node.getNodeType() in ['prop','bomb']:
            self.suckObjects.append(node)
        
        for i in self.suckObjects:
            if i.exists():
                if i.sticky:
                    i.sticky = False
                    i.extraAcceleration = (0,10,0)
                else:
                    i.extraAcceleration = ((self.position[0] - i.position[0])*8,(self.position[1] - i.position[1])*25,(self.position[2] - i.position[2])*8)
        
    def handleMessage(self,m):
        if isinstance(m,bs.DieMessage):
            if self.node.exists():
                self.node.delete()
            if self.suckRadius.exists():
                self.suckRadius.delete()
            self._updTimer = None
            self._suckTimer = None
            self.sound2 = None
            self.suckObjects = []
        elif isinstance(m,bs.OutOfBoundsMessage):
            self.node.handleMessage(bs.DieMessage())
        elif isinstance(m,BlackHoleMessage):
            print 'ww'
            node = bs.getCollisionInfo('opposingNode')
            bs.Blast(position = self.position,blastType = 'turret').autoRetain()
            if not node.invincible:
                node.shattered = 2
                
class MagneticZone(bs.Actor):
    def __init__(self,position = (0,1,0),scale = 10,infinity = False,owner = None):
        bs.Actor.__init__(self)
        self.shields = []
        
        self.position = (position[0],position[1],position[2])
        self.scale = scale
        self.suckObjects = []
        self.owner = owner
        
        self.blackHoleMaterial = bs.Material()
        self.suckMaterial = bs.Material()
                                                  
        self.suckMaterial.addActions(conditions=(('theyHaveMaterial', bs.getSharedObject('objectMaterial'))),actions=(("modifyPartCollision","collide",True),
                                                      ("modifyPartCollision","physical",False),
                                                      ("call","atConnect", self.touchedObjSuck)))
                              
        self.suckRadius = bs.newNode('region',
                       attrs={'position':(self.position[0],self.position[1],self.position[2]),
                              'scale':(scale,scale,scale),
                              'type':'sphere',
                              'materials':[self.suckMaterial]})
                              
        
        if not infinity:
            self._dieTimer = bs.Timer(30000,bs.WeakCall(self.finish))
        bsUtils.animateArray(self.suckRadius,"scale",3,{0:(0,0,0),300:(self.scale*8,self.scale*8,self.scale*8)},True)
        
    def finish(self):
        self.suckRadius.delete()
        self.suckRadius.handleMessage(bs.DieMessage())
		
    def touchedObjSuck(self):
        node = bs.getCollisionInfo('opposingNode')
        if node.getNodeType() in ['prop']:#,'bomb']:
            self.suckObjects.append(node)

        if self.owner.exists():
            for i in self.suckObjects:
                if i.exists():
                    if i.sticky:
                        i.sticky = False
                        i.extraAcceleration = (0,10,0)
                    else:
                        i.extraAcceleration = ((self.owner.position[0] - i.position[0])*25,(self.owner.position[1] - i.position[1])*25,(self.owner.position[2] - i.position[2])*25)
        else: self.finish()

class Artillery(object):
    def __init__(self,position = (0,1,0),target = None,owner = None,bombType = 'impact',sourcePlayer = None):
    
        self.position = position
        self.owner = owner
        self.target = target
        self.bombType = bombType
        self.sourcePlayer = sourcePlayer
        self.radius = 60
        
        
        self.maxHeight = bs.getActivity().getMap().getDefBoundBox('levelBounds')

        
        self.aimZone = bs.Material()
        self.aimZone.addActions(conditions=(('theyHaveMaterial', bs.getSharedObject('playerMaterial'))),actions=(("modifyPartCollision","collide",True),
                                                      ("modifyPartCollision","physical",False),
                                                      ("call","atConnect", self.touchedSpaz)))
        
        
        self.node = bs.newNode('region',
                       attrs={'position':self.position,
                              'scale':(0.5,0.5,0.5),
                              'type':'sphere',
                              'materials':[self.aimZone]})
        
        bsUtils.animateArray(self.node,"scale",3,{0:(0.5,0.5,0.5),100:(self.radius,self.radius,self.radius)})
        bs.gameTimer(101,self.node.delete)
        bs.gameTimer(102,self.strike)
        
    def touchedSpaz(self):
        node = bs.getCollisionInfo('opposingNode')
        if self.owner is not None:
            if not node == self.owner:
                self.target = node
                self.node.materials = [bs.Material()]
                bs.gameTimer(300,self.node.delete)

        
    def strike(self):
        if self.target is not None:
            def launchBomb():
                if self.target is not None and self.target.exists():
                    self.pos = self.target.position
                    b = bs.Bomb(position = self.position,velocity = (0,5,0),bombType = self.bombType,napalm = True).autoRetain()
                    b.node.extraAcceleration = (0,700,0)
                    b.node.velocity = (b.node.velocity[0]+(self.pos[0]-b.node.position[0]),10, b.node.velocity[2]+(self.pos[2]-b.node.position[2]))
                    bs.playSound(bs.getSound('Aim'))
            bs.gameTimer(100,bs.Call(launchBomb))
            bs.gameTimer(200,bs.Call(launchBomb))
            bs.gameTimer(300,bs.Call(launchBomb))
            bs.gameTimer(400,bs.Call(launchBomb))
            bs.gameTimer(500,bs.Call(launchBomb))
            bs.gameTimer(700,bs.Call(launchBomb))
            bs.gameTimer(900,bs.Call(self.drop))
        
    def drop(self):
        print 'droped'
        def launchBombDrop():
            bs.playSound(bs.getSound('Aim'))
            b = bs.Bomb(position = (self.pos[0]+(-2+random.random()*4),self.maxHeight[4],self.pos[2]+(-2+random.random()*4)),velocity = (0,-100,0),bombType = self.bombType,sourcePlayer = self.sourcePlayer).autoRetain()
            b.node.extraAcceleration = (0,-100,0)
        bs.gameTimer(100,bs.Call(launchBombDrop))
        bs.gameTimer(300,bs.Call(launchBombDrop))
        bs.gameTimer(500,bs.Call(launchBombDrop))
        bs.gameTimer(700,bs.Call(launchBombDrop))
        bs.gameTimer(900,bs.Call(launchBombDrop))
        bs.gameTimer(1000,bs.Call(launchBombDrop))
        
class Toxic(bs.Actor):
    def __init__(self,position = (0,1,0),radius=2.5,time = 8000):
        self.position = position
        bs.Actor.__init__(self)
        
        self.poisonMaterial = bs.Material()
        self.poisonMaterial.addActions(conditions=(('theyHaveMaterial', bs.getSharedObject('playerMaterial'))),actions=(("modifyPartCollision","collide",True),
                                                      ("modifyPartCollision","physical",False),
                                                      ("call","atConnect", self.touchedSpaz)))
        self.radius = radius

        self.node = bs.newNode('region',
                       attrs={'position':(self.position[0],self.position[1],self.position[2]),
                              'scale':(0.1,0.1,0.1),
                              'type':'sphere',
                              'materials':[self.poisonMaterial]})
                              
        self.visualRadius = bs.newNode('shield',attrs={'position':self.position,'color':(0.3,1.2,0.3),'radius':0.1})
        
        bsUtils.animate(self.visualRadius,"radius",{0:0,500:self.radius*2})
        bsUtils.animateArray(self.node,"scale",3,{0:(0,0,0),500:(self.radius,self.radius,self.radius)},True)
        
        bs.gameTimer(7700,bs.WeakCall(self.anim))
        bs.gameTimer(time,self.node.delete)
        bs.gameTimer(time,self.visualRadius.delete)
        
    def anim(self):
        bsUtils.animate(self.visualRadius,"radius",{0:self.radius*2,200:0})
        bsUtils.animateArray(self.node,"scale",3,{0:(self.radius,self.radius,self.radius),200:(0,0,0)})
        
    def touchedSpaz(self):
        node = bs.getCollisionInfo('opposingNode')
        node.handleMessage("knockout",5000)
        
    def delete(self):
        self.node.delete()
        self.visualRadius.delete()
        
class Poison(bs.Actor):
    def __init__(self,position = (0,1,0),radius=2.2,owner = None):
        ######################################
        # Dont ask me, how in works!         #
        # I am too lazy to use a factory!(2) #
        ######################################
        self.position = position
        bs.Actor.__init__(self)
        self.poisonMaterial = bs.Material()
        self.radius = radius
        self.poisonMaterial.addActions(conditions=(('theyHaveMaterial', bs.getSharedObject('playerMaterial'))),actions=(("modifyPartCollision","collide",True),
                                                      ("modifyPartCollision","physical",False),
                                                      ("call","atConnect", self.touchedSpaz)))
        self.node = bs.newNode('region',
                       owner=owner,
                       attrs={'position':(self.position[0],self.position[1],self.position[2]),
                              'scale':(0.1,0.1,0.1),
                              'type':'sphere',
                              'materials':[self.poisonMaterial]})
        self.visualRadius = bs.newNode('shield',attrs={'position':self.position,'color':(0.3,0.3,0),'radius':0.1})
        bsUtils.animate(self.visualRadius,"radius",{0:0,200:self.radius*2,400:0})
        bsUtils.animateArray(self.node,"scale",3,{0:(0,0,0),200:(self.radius,self.radius,self.radius),400:(0,0,0)})
        bs.gameTimer(250,self.node.delete)
        bs.gameTimer(250,self.visualRadius.delete)
        bs.emitBGDynamics(position=self.position,count=100,emitType='tendrils',tendrilType='smoke')
        
    def touchedSpaz(self):
        node = bs.getCollisionInfo('opposingNode')
        node.getDelegate().curse()
        
    def delete(self):
        self.node.delete()
        self.visualRadius.delete()
        
class ShockWave(bs.Actor):
    def __init__(self,position = (0,1,0),radius=2,speed = 200):
        bs.Actor.__init__(self)
        self.position = position
        
        self.shockWaveMaterial = bs.Material()
        self.shockWaveMaterial.addActions(conditions=(('theyHaveMaterial', bs.getSharedObject('playerMaterial'))),actions=(("modifyPartCollision","collide",True),
                                                      ("modifyPartCollision","physical",False),
                                                      ("call","atConnect", self.touchedSpaz)))
        self.shockWaveMaterial.addActions(conditions=(('theyHaveMaterial', bs.getSharedObject('objectMaterial')),'and',('theyDontHaveMaterial', bs.getSharedObject('playerMaterial'))),actions=(("modifyPartCollision","collide",True),
                                                      ("modifyPartCollision","physical",False),
                                                      ("call","atConnect", self.touchedObj)))
        self.radius = radius

        self.node = bs.newNode('region',
                       attrs={'position':(self.position[0],self.position[1],self.position[2]),
                              'scale':(0.1,0.1,0.1),
                              'type':'sphere',
                              'materials':[self.shockWaveMaterial]})
                              
        self.visualRadius = bs.newNode('shield',attrs={'position':self.position,'color':(0.05,0.05,0.1),'radius':0.1})
        
        bsUtils.animate(self.visualRadius,"radius",{0:0,speed:self.radius*2})
        bsUtils.animateArray(self.node,"scale",3,{0:(0,0,0),speed:(self.radius,self.radius,self.radius)},True)
        
        bs.gameTimer(speed+1,self.node.delete)
        bs.gameTimer(speed+1,self.visualRadius.delete)
        
        
    def touchedSpaz(self):
        node = bs.getCollisionInfo('opposingNode')
        
        s = node.getDelegate()._punchPowerScale
        node.getDelegate()._punchPowerScale -= 0.3
        def re():
            node.getDelegate()._punchPowerScale = s
        bs.gameTimer(2000,re)
        
        bs.playSound(bs.getSound(random.choice(['electro1','electro2','electro3'])))
        node.handleMessage("impulse",node.position[0],node.position[1],node.position[2],
                                    -node.velocity[0],-node.velocity[1],-node.velocity[2],
                                    200,200,0,0,-node.velocity[0],-node.velocity[1],-node.velocity[2])
        flash = bs.newNode("flash",
                                   attrs={'position':node.position,
                                          'size':0.7,
                                          'color':(0,0.4+random.random(),1)})
                                          
        explosion = bs.newNode("explosion",
                               attrs={'position':node.position,
                                      'velocity':(node.velocity[0],max(-1.0,node.velocity[1]),node.velocity[2]),
                                      'radius':0.4,
                                      'big':True,
                                      'color':(0.3,0.3,1)})
        bs.gameTimer(400,explosion.delete)
                                          
        bs.emitBGDynamics(position=node.position,count=20,scale=0.5,spread=0.5,chunkType='spark')
        bs.gameTimer(60,flash.delete)
    
    def touchedObj(self):
        node = bs.getCollisionInfo('opposingNode')
        bs.playSound(bs.getSound(random.choice(['electro1','electro2','electro3'])))

        node.handleMessage("impulse",node.position[0]+random.uniform(-2,2),node.position[1]+random.uniform(-2,2),node.position[2]+random.uniform(-2,2),
                                    -node.velocity[0]+random.uniform(-2,2),-node.velocity[1]+random.uniform(-2,2),-node.velocity[2]+random.uniform(-2,2),
                                    100,100,0,0,-node.velocity[0]+random.uniform(-2,2),-node.velocity[1]+random.uniform(-2,2),-node.velocity[2]+random.uniform(-2,2))
        flash = bs.newNode("flash",
                                   attrs={'position':node.position,
                                          'size':0.4,
                                          'color':(0,0.4+random.random(),1)})
                                          
        explosion = bs.newNode("explosion",
                               attrs={'position':node.position,
                                      'velocity':(node.velocity[0],max(-1.0,node.velocity[1]),node.velocity[2]),
                                      'radius':0.4,
                                      'big':True,
                                      'color':(0.3,0.3,1)})
        bs.gameTimer(400,explosion.delete)
                                          
        bs.emitBGDynamics(position=node.position,count=20,scale=0.5,spread=0.5,chunkType='spark')
        bs.gameTimer(60,flash.delete)
        
    def delete(self):
        self.node.delete()
        self.visualRadius.delete()
        
class Portal(bs.Actor):
    def __init__(self,position1 = (0,1,0),position2 = (3,1,0),color = (random.random(),random.random(),random.random())):
        bs.Actor.__init__(self)
        
        self.radius = 1.1
        self.position1 = position1
        self.position2 = position2
        self.cooldown = False
        
        self.portal1Material = bs.Material()
        self.portal1Material.addActions(conditions=(('theyHaveMaterial', bs.getSharedObject('playerMaterial'))),actions=(("modifyPartCollision","collide",True),
                                                      ("modifyPartCollision","physical",False),
                                                      ("call","atConnect", self.Portal1)))
                                                      
        self.portal2Material = bs.Material()
        self.portal2Material.addActions(conditions=(('theyHaveMaterial', bs.getSharedObject('playerMaterial'))),actions=(("modifyPartCollision","collide",True),
                                                      ("modifyPartCollision","physical",False),
                                                      ("call","atConnect", self.Portal2)))
                                                      
        self.portal1Material.addActions(conditions=(('theyHaveMaterial', bs.getSharedObject('objectMaterial')),'and',('theyDontHaveMaterial', bs.getSharedObject('playerMaterial'))),actions=(("modifyPartCollision","collide",True),
                                                      ("modifyPartCollision","physical",False),
                                                      ("call","atConnect", self.objPortal1)))
                                                      
        self.portal2Material.addActions(conditions=(('theyHaveMaterial', bs.getSharedObject('objectMaterial')),'and',('theyDontHaveMaterial', bs.getSharedObject('playerMaterial'))),actions=(("modifyPartCollision","collide",True),
                                                      ("modifyPartCollision","physical",False),
                                                      ("call","atConnect", self.objPortal2)))
                                                      
                                                 
        self.node1 = bs.newNode('region',
                       attrs={'position':(self.position1[0],self.position1[1],self.position1[2]),
                              'scale':(0.1,0.1,0.1),
                              'type':'sphere',
                              'materials':[self.portal1Material]})
        self.visualRadius = bs.newNode('shield',attrs={'position':self.position1,'color':color,'radius':0.1})
        bsUtils.animate(self.visualRadius,"radius",{0:0,500:self.radius*2})
        bsUtils.animateArray(self.node1,"scale",3,{0:(0,0,0),500:(self.radius,self.radius,self.radius)})
        
        
        self.node2 = bs.newNode('region',
                       attrs={'position':(self.position2[0],self.position2[1],self.position2[2]),
                              'scale':(0.1,0.1,0.1),
                              'type':'sphere',
                              'materials':[self.portal2Material]})
        self.visualRadius2 = bs.newNode('shield',attrs={'position':self.position2,'color':color,'radius':0.1})
        bsUtils.animate(self.visualRadius2,"radius",{0:0,500:self.radius*2})
        bsUtils.animateArray(self.node2,"scale",3,{0:(0,0,0),500:(self.radius,self.radius,self.radius)})
        
    def cooldown1(self):
        self.cooldown = True
        def off():
            self.cooldown = False
        bs.gameTimer(10,off)
        
        
    def Portal1(self):
        node = bs.getCollisionInfo('opposingNode')
        node.handleMessage(bs.StandMessage(position = self.node2.position))
        
    def Portal2(self):
        node = bs.getCollisionInfo('opposingNode')
        node.handleMessage(bs.StandMessage(position = self.node1.position))
        
    def objPortal1(self):
        node = bs.getCollisionInfo('opposingNode')
        v = node.velocity
        if not self.cooldown:
            node.position = self.position2
            self.cooldown1()
        def vel():
            node.velocity = v
        bs.gameTimer(10,vel)
    
    def objPortal2(self):
        node = bs.getCollisionInfo('opposingNode')
        v = node.velocity
        if not self.cooldown:
            node.position = self.position1
            self.cooldown1()
        def vel():
            node.velocity = v
        bs.gameTimer(10,vel)

class Spaz(bs.Actor):
    """
    category: Game Flow Classes
    
    Base class for various Spazzes.
    A Spaz is the standard little humanoid character in the game.
    It can be controlled by a player or by AI, and can have
    various different appearances.  The name 'Spaz' is not to be
    confused with the 'Spaz' character in the game, which is just
    one of the skins available for instances of this class.

    Attributes:

       node
          The 'spaz' bs.Node.
    """
    pointsMult = 1
    curseTime = 5000
    defaultBombCount = 1
    defaultBombType = 'normal'
    defaultBoxingGloves = False
    defaultShieldForBot = False
    defaultShields = False
    defaultShieldLevel4 = False
    defaultShieldLevel3 = False
    defaultShieldLevel2 = False
    defaultShieldLevel1 = False

    def __init__(self, color=(1, 1, 1), highlight=(0.5, 0.5, 0.5),
                 character="Spaz", sourcePlayer=None, startInvincible=True,
                 canAcceptPowerups=True, powerupsExpire=False, demoMode=False):
        """
        Create a new spaz with the requested color, character, etc.
        """
        
        bs.Actor.__init__(self)
        activity = self.getActivity()
        
        factory = self.getFactory()

        # we need to behave slightly different in the tutorial
        self._demoMode = demoMode
        
        self.playBigDeathSound = False

        # translate None into empty player-ref
        if sourcePlayer is None: sourcePlayer = bs.Player(None)

        # scales how much impacts affect us (most damage calcs)
        self._impactScale = 1.0
        
        self.sourcePlayer = sourcePlayer
        self._dead = False
        if self._demoMode: # preserve old behavior
            self._punchPowerScale = gBasePunchPowerScale
        else:
            self._punchPowerScale = factory.punchPowerScale
        self.fly = bs.getSharedObject('globals').happyThoughtsMode
        self._hockey = activity._map.isHockey
        self._punchedNodes = set()
        self._cursed = False
        self._connectedToPlayer = None

        materials = [factory.spazMaterial,
                     bs.getSharedObject('objectMaterial'),
                     bs.getSharedObject('playerMaterial')]
        
        rollerMaterials = [factory.rollerMaterial,
                           bs.getSharedObject('playerMaterial')]
        
        extrasMaterials = []
        
        if canAcceptPowerups:
            pam = bs.Powerup.getFactory().powerupAcceptMaterial
            materials.append(pam)
            rollerMaterials.append(pam)
            extrasMaterials.append(pam)

        media = factory._getMedia(character)
        self.node = bs.newNode(
            type="spaz",
            delegate=self,
            attrs={'color':color,
                   'behaviorVersion':0 if demoMode else 1,
                   'demoMode':True if demoMode else False,
                   'highlight':highlight,
                   'jumpSounds':media['jumpSounds'],
                   'attackSounds':media['attackSounds'],
                   'impactSounds':media['impactSounds'],
                   'deathSounds':media['deathSounds'],
                   'pickupSounds':media['pickupSounds'],
                   'fallSounds':media['fallSounds'],
                   'colorTexture':media['colorTexture'],
                   'colorMaskTexture':media['colorMaskTexture'],
                   'headModel':media['headModel'],
                   'torsoModel':media['torsoModel'],
                   'pelvisModel':media['pelvisModel'],
                   'upperArmModel':media['upperArmModel'],
                   'foreArmModel':media['foreArmModel'],
                   'handModel':media['handModel'],
                   'upperLegModel':media['upperLegModel'],
                   'lowerLegModel':media['lowerLegModel'],
                   'toesModel':media['toesModel'],
                   'style':factory._getStyle(character),
                   'fly':self.fly,
                   'hockey':self._hockey,
                   'materials':materials,
                   'rollerMaterials':rollerMaterials,
                   'extrasMaterials':extrasMaterials,
                   'punchMaterials':(factory.punchMaterial,
                                     bs.getSharedObject('attackMaterial')),
                   'pickupMaterials':(factory.pickupMaterial,
                                      bs.getSharedObject('pickupMaterial')),
                   'invincible':startInvincible,
                   'sourcePlayer':sourcePlayer})
        self.shield = None

        if startInvincible:
            def _safeSetAttr(node, attr, val):
                if node.exists(): setattr(node, attr, val)
            bs.gameTimer(1000, bs.Call(_safeSetAttr, self.node,
                                       'invincible', False))

        self.hitPoints = 1000
        self.hitPointsMax = 1000
        self.bombCount = self.defaultBombCount
        self._maxBombCount = self.defaultBombCount
        self.bombTypeDefault = self.defaultBombType
        self.bombType = self.bombTypeDefault
        self.landMineCount = 0
        self.powerupBombCount = 0
        self.dirigidaCount = 0
##############################################                 
        if settings.charactersWithPowers == False:
            self.bombType = 'tntImpact' if character == 'Suicida' else 'BdV' if character == 'Health' else 'BdM' if character == 'Curse' else 'sticky' if character == 'Sticky' else 'ice' if character == 'Ice' else 'impact' if character == 'Impact' else 'landMine' if character == 'LandMine' else 'mostro' if character == 'Mostro' else 'fireBomb' if character == 'Fireman' else self.bombTypeDefault
            self.setBombCount(5) if character == 'Suicida' else self.setBombCount(2) if character == 'Health' else self.setBombCount(3) if character == 'Bomb' else self.setBombCount(2) if character == 'Mostro' else self.setBombCount(2) if character == 'Fireman' else self.defaultBombCount
            self.curseTime=-1 if character == 'Suicida' else None
            self.curse() if character == 'Suicida' else None
            self.equipShieldForBot() if character == 'Shield' else None
            self.equipBoxingGloves() if character == 'Punch' else None
            self.node.hockey = True if character == 'Speed' else False
        else:
        	None

#Esto hara que el hermano de Oso maton sea brillante, pero esto puede variar :v#
        if character == 'Oso Espectro':
            self.node.color = (self.node.color[0]*6,self.node.color[1]*6,self.node.color[2]*6)
            self.node.highlight = (self.node.highlight[0]*6,self.node.highlight[1]*6,self.node.highlight[2]*6)
#Es un suicida :v.
        if character == 'Suicida':
            bs.animateArray(self.node,'color',3,{1000:(1,1,1),300:(1*3,0,0),1000:(1,1,1)},True)
            #self.bombType = 'tntImpact'
            #self.setBombCount(5)
            #self.curseTime=-1
            #self.curse()
#Powerups...
        #if character == 'Health':
            #self.bombType = 'BdV'
            #self.setBombCount(2)
        #if character == 'Curse':
            #self.bombType = 'BdM'
        #if character == 'Sticky':
            #self.bombType = 'sticky'
        #if character == 'Ice':
            #self.bombType = 'ice'
        #if character == 'Impact':
            #self.bombType = 'impact'
        #if character == 'LandMine':
            #self.bombType = 'landMine'
        #if character == 'Shield':
            #self.equipShieldForBot()
        #if character == 'Punch':
            #self.equipBoxingGloves()
        #if character == 'Speed':
            #self.node.hockey = True
        #if character == 'Bomb':
            #self.setBombCount(3)
#Es simplemente feo. Pero tenga cuidado te puede convertir en un mostro...
        #if character == 'Mostro':
            #self.bombType = 'mostro'
            #self.setBombCount(2)
#Es simplemente un hombre que pude lanzar bolas de fuego fakes...
        #if character == 'Fireman':
            #self.bombType = 'fireBomb'
            #self.setBombCount(2)
                
        self.blastRadius = 2.0
        self.powerupsExpire = powerupsExpire
        if self._demoMode: # preserve old behavior
            self._punchCooldown = gBasePunchCooldown
        else:
            self._punchCooldown = factory.punchCooldown
        self._jumpCooldown = 250
        self._pickupCooldown = 0
        self._bombCooldown = 0
        self._hasBoxingGloves = False
        if self.defaultBoxingGloves: self.equipBoxingGloves()
        self.lastPunchTime = -9999
        self.lastJumpTime = -9999
        self.lastPickupTime = -9999
        self.lastRunTime = -9999
        self._lastRunValue = 0
        self.lastBombTime = -9999
        self._turboFilterTimes = {}
        self._turboFilterTimeBucket = 0
        self._turboFilterCounts = {}
        self.frozen = False
        self.alto = False
        self.bug = False
        self.shattered = False
        self._lastHitTime = None
        self._numTimesHit = 0
        self._bombHeld = False
        
        
        if self.defaultShieldLevel1: self.equipShieldLevel1()
        elif self.defaultShieldLevel2: self.equipShieldLevel2()
        elif self.defaultShieldLevel3: self.equipShieldLevel3()
        elif self.defaultShieldLevel4: self.equipShieldLevel4()
        elif self.defaultShieldForBot: self.equipShieldForBot()
        if self.defaultShields: self.equipShields()
        self._droppedBombCallbacks = []

        # deprecated stuff.. need to make these into lists
        self.punchCallback = None
        self.pickUpPowerupCallback = None

    def onFinalize(self):
        bs.Actor.onFinalize(self)

        # release callbacks/refs so we don't wind up with dependency loops..
        self._droppedBombCallbacks = []
        self.punchCallback = None
        self.pickUpPowerupCallback = None
        
    def addDroppedBombCallback(self, call):
        """
        Add a call to be run whenever this Spaz drops a bomb.
        The spaz and the newly-dropped bomb are passed as arguments.
        """
        self._droppedBombCallbacks.append(call)
                            
    def isAlive(self):
        """
        Method override; returns whether ol' spaz is still kickin'.
        """
        return not self._dead

    @classmethod
    def getFactory(cls):
        """
        Returns the shared bs.SpazFactory object, creating it if necessary.
        """
        activity = bs.getActivity()
        if activity is None: raise Exception("no current activity")
        try: return activity._sharedSpazFactory
        except Exception:
            f = activity._sharedSpazFactory = SpazFactory()
            return f

    def exists(self):
        return self.node.exists()

    def _hideScoreText(self):
        if self._scoreText.exists():
            bs.animate(self._scoreText, 'scale',
                       {0:self._scoreText.scale, 200:0})

    def _turboFilterAddPress(self, source):
        """
        Can pass all button presses through here; if we see an obscene number
        of them in a short time let's shame/pushish this guy for using turbo
        """
        t = bs.getNetTime()
        tBucket = int(t/1000)
        if tBucket == self._turboFilterTimeBucket:
            # add only once per timestep (filter out buttons triggering
            # multiple actions)
            if t != self._turboFilterTimes.get(source, 0):
                self._turboFilterCounts[source] = \
                    self._turboFilterCounts.get(source, 0) + 1
                self._turboFilterTimes[source] = t
                # (uncomment to debug; prints what this count is at)
                # bs.screenMessage( str(source) + " "
                #                   + str(self._turboFilterCounts[source]))
                if self._turboFilterCounts[source] == 15:
                    
                    # knock 'em out.  That'll learn 'em.
                    self.node.handleMessage("knockout", 500.0)

                    # also issue periodic notices about who is turbo-ing
                    realTime = bs.getRealTime()
                    global gLastTurboSpamWarningTime
                    if realTime > gLastTurboSpamWarningTime + 30000:
                        gLastTurboSpamWarningTime = realTime
                        bs.screenMessage(
                            bs.Lstr(translate=('statements',
                                               ('Warning to ${NAME}:  '
                                                'turbo / button-spamming knocks'
                                                ' you out.')),
                                    subs=[('${NAME}', self.node.name)]),
                            color=(1, 0.5, 0))
                        bs.playSound(bs.getSound('error'))
        else:
            self._turboFilterTimes = {}
            self._turboFilterTimeBucket = tBucket
            self._turboFilterCounts = {source:1}
        
    def setScoreText(self, t, color=(1, 1, 0.4), flash=False):
        """
        Utility func to show a message momentarily over our spaz that follows
        him around; Handy for score updates and things.
        """
        colorFin = bs.getSafeColor(color)[:3]
        if not self.node.exists(): return
        try: exists = self._scoreText.exists()
        except Exception: exists = False
        if not exists:
            startScale = 0.0
            m = bs.newNode('math', owner=self.node, attrs={ 'input1':(0, 1.4, 0),
                                                            'operation':'add' })
            self.node.connectAttr('torsoPosition', m, 'input2')
            self._scoreText = bs.newNode('text',
                                          owner=self.node,
                                          attrs={'text':t,
                                                 'inWorld':True,
                                                 'shadow':1.0,
                                                 'flatness':1.0,
                                                 'color':colorFin,
                                                 'scale':0.02,
                                                 'hAlign':'center'})
            m.connectAttr('output', self._scoreText, 'position')
        else:
            self._scoreText.color = colorFin
            startScale = self._scoreText.scale
            self._scoreText.text = t
        if flash:
            combine = bs.newNode("combine", owner=self._scoreText,
                                 attrs={'size':3})
            sc = 1.8
            offs = 0.5
            t = 300
            for i in range(3):
                c1 = offs+sc*colorFin[i]
                c2 = colorFin[i]
                bs.animate(combine, 'input'+str(i), {0.5*t:c2,
                                                   0.75*t:c1,
                                                   1.0*t:c2})
            combine.connectAttr('output', self._scoreText, 'color')
            
        bs.animate(self._scoreText, 'scale', {0:startScale, 200:0.02})
        self._scoreTextHideTimer = bs.Timer(1000,
                                            bs.WeakCall(self._hideScoreText))
        
    def onJumpPress(self):
        """
        Called to 'press jump' on this spaz;
        used by player or AI connections.
        """
        if not self.node.exists(): return
        t = bs.getGameTime()
        if t - self.lastJumpTime >= self._jumpCooldown:
            self.node.jumpPressed = True
            self.lastJumpTime = t
        self._turboFilterAddPress('jump')
        bs.statAdd('Jumps Countered')

    def onJumpRelease(self):
        """
        Called to 'release jump' on this spaz;
        used by player or AI connections.
        """
        if not self.node.exists(): return
        self.node.jumpPressed = False

    def onPickUpPress(self):
        """
        Called to 'press pick-up' on this spaz;
        used by player or AI connections.
        """
        if not self.node.exists(): return
        t = bs.getGameTime()
        if t - self.lastPickupTime >= self._pickupCooldown:
            self.node.pickUpPressed = True
            self.lastPickupTime = t
        self._turboFilterAddPress('pickup')
        bs.statAdd('Pickups Countered')

    def onPickUpRelease(self):
        """
        Called to 'release pick-up' on this spaz;
        used by player or AI connections.
        """
        if not self.node.exists(): return
        self.node.pickUpPressed = False

    def _onHoldPositionPress(self):
        """
        Called to 'press hold-position' on this spaz;
        used for player or AI connections.
        """
        if not self.node.exists(): return
        self.node.holdPositionPressed = True
        self._turboFilterAddPress('holdposition')

    def _onHoldPositionRelease(self):
        """
        Called to 'release hold-position' on this spaz;
        used for player or AI connections.
        """
        if not self.node.exists(): return
        self.node.holdPositionPressed = False

    def onPunchPress(self):
        """
        Called to 'press punch' on this spaz;
        used for player or AI connections.
        """
        if (not self.node.exists()
            or self.frozen
            or self.node.knockout > 0.0): return
        t = bs.getGameTime()
        if t - self.lastPunchTime >= self._punchCooldown:
            if self.punchCallback is not None:
                self.punchCallback(self)
            self._punchedNodes = set() # reset this..
            self.lastPunchTime = t
            self.node.punchPressed = True
            if not self.node.holdNode.exists():
                bs.gameTimer(100, bs.WeakCall(self._safePlaySound,
                                              self.getFactory().swishSound,
                                              0.8))
        self._turboFilterAddPress('punch')
        bs.statAdd('Punchs Countered')

    def _safePlaySound(self, sound, volume):
        """
        Plays a sound at our position if we exist.
        """
        if self.node.exists():
            bs.playSound(sound, volume, self.node.position)
        
    def onPunchRelease(self):
        """
        Called to 'release punch' on this spaz;
        used for player or AI connections.
        """
        if not self.node.exists(): return
        self.node.punchPressed = False

    def onBombPress(self):
        """
        Called to 'press bomb' on this spaz;
        used for player or AI connections.
        """
        if not self.node.exists(): return
        
        if self._dead or self.frozen: return
        if self.node.knockout > 0.0: return
        t = bs.getGameTime()
        if t - self.lastBombTime >= self._bombCooldown:
            self.lastBombTime = t
            self.node.bombPressed = True
            if not self.node.holdNode.exists(): self.dropBomb()
        self._turboFilterAddPress('bomb')
        bs.statAdd('Bombs Countered')

    def onBombRelease(self):
        """
        Called to 'release bomb' on this spaz; 
        used for player or AI connections.
        """
        if not self.node.exists(): return
        self.node.bombPressed = False

    def onRun(self, value):
        """
        Called to 'press run' on this spaz;
        used for player or AI connections.
        """
        if not self.node.exists(): return

        t = bs.getGameTime()
        self.lastRunTime = t
        if self.bug == True: value = value * 80
        self.node.run = value

        # filtering these events would be tough since its an analog
        # value, but lets still pass full 0-to-1 presses along to
        # the turbo filter to punish players if it looks like they're turbo-ing
        if self._lastRunValue < 0.01 and value > 0.99:
            self._turboFilterAddPress('run')
            
        self._lastRunValue = value
            

    def onFlyPress(self):
        """
        Called to 'press fly' on this spaz;
        used for player or AI connections.
        """
        if not self.node.exists(): return
        # not adding a cooldown time here for now; slightly worried
        # input events get clustered up during net-games and we'd wind up
        # killing a lot and making it hard to fly.. should look into this.
        self.node.flyPressed = True
        self._turboFilterAddPress('fly')

    def onFlyRelease(self):
        """
        Called to 'release fly' on this spaz;
        used for player or AI connections.
        """
        if not self.node.exists(): return
        self.node.flyPressed = False

    def onMove(self, x, y):
        """
        Called to set the joystick amount for this spaz;
        used for player or AI connections.
        """
        if not self.node.exists(): return
        self.node.handleMessage("move", x, y)
        
    def onMoveUpDown(self, value):
        """
        Called to set the up/down joystick amount on this spaz;
        used for player or AI connections.
        value will be between -32768 to 32767
        WARNING: deprecated; use onMove instead.
        """
        if not self.node.exists(): return
        if self.alto == True: value = value * 0
        self.node.moveUpDown = value

    def onMoveLeftRight(self, value):
        """
        Called to set the left/right joystick amount on this spaz;
        used for player or AI connections.
        value will be between -32768 to 32767
        WARNING: deprecated; use onMove instead.
        """
        if not self.node.exists(): return
        if self.alto == True: value = value * 0
        self.node.moveLeftRight = value

    def onPunched(self, damage):
        """
        Called when this spaz gets punched.
        """
        pass

    def getDeathPoints(self, how):
        'Get the points awarded for killing this spaz'
        numHits = float(max(1, self._numTimesHit))
        # base points is simply 10 for 1-hit-kills and 5 otherwise
        importance = 2 if numHits < 2 else 1
        return ((10 if numHits < 2 else 5) * self.pointsMult, importance)
        

    def curse(self):
        """
        Give this poor spaz a curse;
        he will explode in 5 seconds.
        """
        if not self._cursed:
            factory = self.getFactory()
            self._cursed = True
            # add the curse material..
            for attr in ['materials', 'rollerMaterials']:
                materials = getattr(self.node, attr)
                if not factory.curseMaterial in materials:
                    setattr(self.node, attr,
                            materials + (factory.curseMaterial,))

            # -1 specifies no time limit
            if self.curseTime == -1:
                self.node.curseDeathTime = -1
            else:
                self.node.curseDeathTime = bs.getGameTime()+5000
                bs.gameTimer(5000, bs.WeakCall(self.curseExplode))
                
    def curse2(self):
        """
        Give this poor spaz a curse;
        he will explode in 10 seconds.
        """
        if not self._cursed:
            factory = self.getFactory()
            self._cursed = True
            # add the curse material..
            for attr in ['materials', 'rollerMaterials']:
                materials = getattr(self.node, attr)
                if not factory.curseMaterial in materials:
                    setattr(self.node, attr,
                            materials + (factory.curseMaterial,))

            # -1 specifies no time limit
            if self.curseTime == -1:
                self.node.curse2DeathTime = -1
            else:
                self.node.curseDeathTime = bs.getGameTime()+10000
                bs.gameTimer(10000, bs.WeakCall(self.curseExplode))

    def equipBoxingGloves(self):
        """
        Give this spaz some boxing gloves.
        """
        self.node.boxingGloves = 1
        if self._demoMode: # preserve old behavior
            self._punchPowerScale = 1.7
            self._punchCooldown = 300
        else:
            factory = self.getFactory()
            self._punchPowerScale = factory.punchPowerScaleGloves
            self._punchCooldown = factory.punchCooldownGloves

    def equipShieldForBot(self):
        """
        Give this spaz a nice energy shield.
        """

        if not self.node.exists():
            bs.printError('Can\'t equip shields; no node.')
            return
        
        factory = self.getFactory()
        if self.shield is None: 
            self.shield = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(0.3, 0.2, 2.0),'radius':1.3})
            self.node.connectAttr('positionCenter',self.shield,'position')
            self.shieldHitPoints = self.shieldHitPointsMax = 650
        self.shieldHitPoints = self.shieldHitPointsMax
        self.shield.hurt = 0
        bs.playSound(factory.shieldUpSound,1.0,position=self.node.position)
        
    def equipShieldLevel1(self):
        """
        Give this spaz a nice energy shield.
        """

        if not self.node.exists():
            bs.printError('Can\'t equip shields; no node.')
            return
        
        factory = self.getFactory()
        if self.shield is None: 
            self.shield = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(1.0,1.0,1.0),'radius':1.3})
            self.node.connectAttr('positionCenter',self.shield,'position')
            self.shieldHitPoints = self.shieldHitPointsMax = 650
        self.shieldHitPoints = self.shieldHitPointsMax
        self.shield.hurt = 0
        bs.playSound(factory.shieldUpSound,1.0,position=self.node.position)
        
    def equipShieldLevel2(self):
        """
        Give this spaz a nice energy shield.
        """

        if not self.node.exists():
            bs.printError('Can\'t equip shields; no node.')
            return
       
        factory = self.getFactory()
        if self.shield is None: 
            self.shield = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(1.0,0.8,0.3),'radius':1.3})
            self.node.connectAttr('positionCenter',self.shield,'position')
            self.shieldHitPoints = self.shieldHitPointsMax = 1300
        self.shieldHitPoints = self.shieldHitPointsMax
        self.shield.hurt = 0
        bs.playSound(factory.shieldUpSound,1.0,position=self.node.position)
                
    def equipShieldLevel3(self):
        """
        Give this spaz a nice energy shield.
        """

        if not self.node.exists():
            bs.printError('Can\'t equip shields; no node.')
            return
        
        factory = self.getFactory()
        if self.shield is None: 
            self.shield = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(1.0,0.3,0.0),'radius':1.3})
            self.node.connectAttr('positionCenter',self.shield,'position')
            self.shieldHitPoints = self.shieldHitPointsMax = 1850
        self.shieldHitPoints = self.shieldHitPointsMax
        self.shield.hurt = 0
        bs.playSound(factory.shieldUpSound,1.0,position=self.node.position)

    def equipShieldLevel4(self):
        """
        Give this spaz a nice energy shield.
        """

        if not self.node.exists():
            bs.printError('Can\'t equip shields; no node.')
            return
        
        factory = self.getFactory()
        if self.shield is None: 
            self.shield = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(1.0*1.3,0.0,0.0),'radius':1.3})
            self.node.connectAttr('positionCenter',self.shield,'position')
            self.shieldHitPoints = self.shieldHitPointsMax = 3100
        self.shieldHitPoints = self.shieldHitPointsMax
        self.shield.hurt = 0
        bs.playSound(factory.shieldUpSound,1.0,position=self.node.position)

    def equipShields(self):
        """
        Give this spaz a nice energy shield.
        """
        colors = [(1.0,1.0,1.0),(1.0,1.0,1.0),(1.0,1.0,1.0),(1.0,1.0,1.0),(1.0,0.8,0.3),(1.0,0.8,0.3),(1.0,0.8,0.3),(1.0,0.3,0.0),(1.0,0.3,0.0),(1.0*1.3,0.0,0.0)]
        shieldColor = random.choice(colors)

        if not self.node.exists():
            bs.printError('Can\'t equip shields; no node.')
            return
        
        factory = self.getFactory()
        if self.shield is None:
            self.shield = bs.newNode('shield',owner=self.node,
                                     attrs={'color':shieldColor,'radius':1.3})
            self.node.connectAttr('positionCenter',self.shield,'position')
            if shieldColor == (1.0,1.0,1.0):
            	bsUtils.PopupText(bs.Lstr(resource='shieldLevel1'),color=(1,1,1),scale=1,position=self.node.position).autoRetain()
            	self.shieldHitPoints = self.shieldHitPointsMax = 650
            elif shieldColor == (1.0,0.8,0.3):
            	bsUtils.PopupText(bs.Lstr(resource='shieldLevel2'),color=(1,1,1),scale=1,position=self.node.position).autoRetain()
            	self.shieldHitPoints = self.shieldHitPointsMax = 1300
            elif shieldColor == (1.0,0.3,0.0):
            	bsUtils.PopupText(bs.Lstr(resource='shieldLevel3'),color=(1,1,1),scale=1,position=self.node.position).autoRetain()
            	self.shieldHitPoints = self.shieldHitPointsMax = 1850
            elif shieldColor == (1.0*1.3,0.0,0.0):
            	bsUtils.PopupText(bs.Lstr(resource='shieldLevel4'),color=(1,1,1),scale=1,position=self.node.position).autoRetain()
            	self.shieldHitPoints = self.shieldHitPointsMax = 3100
       
        self.shieldHitPoints = self.shieldHitPointsMax
        self.shield.hurt = 0
        bs.playSound(factory.shieldUpSound,1.0,position=self.node.position)
        
    def handleMessage(self, msg):
        self._handleMessageSanityCheck()

        if isinstance(msg, bs.PickedUpMessage):
            self.node.handleMessage("hurtSound")
            self.node.handleMessage("pickedUp")
            # this counts as a hit
            self._numTimesHit += 1

        elif isinstance(msg, bs.ShouldShatterMessage):
            # eww; seems we have to do this in a timer or it wont work right
            # (since we're getting called from within update() perhaps?..)
            bs.gameTimer(1, bs.WeakCall(self.shatter))

        elif isinstance(msg, bs.ImpactDamageMessage):
            # eww; seems we have to do this in a timer or it wont work right
            # (since we're getting called from within update() perhaps?..)
            bs.gameTimer(1, bs.WeakCall(self._hitSelf, msg.intensity))

        elif isinstance(msg, bs.PowerupMessage):
            if self._dead: return True
            if self.pickUpPowerupCallback is not None:
                self.pickUpPowerupCallback(self)

            if (msg.powerupType == 'tripleBombs'):
            	bsUtils.PopupText("Bombas Triples",color=(1,1,0),scale=1.2,position=self.node.position).autoRetain()
                tex = bs.Powerup.getFactory().texBomb
                self._flashBillboard(tex)
                self.setBombCount(3)
                if self.powerupsExpire:
                    self.node.miniBillboard1Texture = tex
                    t = bs.getGameTime()
                    self.node.miniBillboard1StartTime = t
                    self.node.miniBillboard1EndTime = t+gPowerupWearOffTime
                    self._multiBombWearOffFlashTimer = bs.Timer(gPowerupWearOffTime-2000,bs.WeakCall(self._multiBombWearOffFlash))
                    self._multiBombWearOffTimer = bs.Timer(gPowerupWearOffTime,bs.WeakCall(self._multiBombWearOff))
            elif msg.powerupType == 'landMines':
            	bsUtils.PopupText("Minas",color=(0,0.7,0.2),scale=1.2,position=self.node.position).autoRetain()
                self.setLandMineCount(min(self.landMineCount+3,3))
            elif msg.powerupType == 'impactBombs':
            	bsUtils.PopupText("Bombas de Impacto",color=(0.7,0,0),scale=1.2,position=self.node.position).autoRetain()
                self.bombType = 'impact'
                tex = self._getBombTypeTex()
                self._flashBillboard(tex)
                if self.powerupsExpire:
                    self.node.miniBillboard2Texture = tex
                    t = bs.getGameTime()
                    self.node.miniBillboard2StartTime = t
                    self.node.miniBillboard2EndTime = t+gPowerupWearOffTime
                    self._bombWearOffFlashTimer = bs.Timer(gPowerupWearOffTime-2000,bs.WeakCall(self._bombWearOffFlash))
                    self._bombWearOffTimer = bs.Timer(gPowerupWearOffTime,bs.WeakCall(self._bombWearOff))
            elif msg.powerupType == 'stickyBombs':
            	bsUtils.PopupText("Bombas Pegajosas",color=(0,0.8,0),scale=1.2,position=self.node.position).autoRetain()
                self.bombType = 'sticky'
                tex = self._getBombTypeTex()
                self._flashBillboard(tex)
                if self.powerupsExpire:
                    self.node.miniBillboard2Texture = tex
                    t = bs.getGameTime()
                    self.node.miniBillboard2StartTime = t
                    self.node.miniBillboard2EndTime = t+gPowerupWearOffTime
                    self._bombWearOffFlashTimer = bs.Timer(gPowerupWearOffTime-2000,bs.WeakCall(self._bombWearOffFlash))
                    self._bombWearOffTimer = bs.Timer(gPowerupWearOffTime,bs.WeakCall(self._bombWearOff))
            elif msg.powerupType == 'upSticky':
            	bsUtils.PopupText("upSticky",color=(0,0.8,0),scale=1.2,position=self.node.position).autoRetain()
                self.bombType = 'upSticky'
                tex = self._getBombTypeTex()
                self._flashBillboard(tex)
                if self.powerupsExpire:
                    self.node.miniBillboard2Texture = tex
                    t = bs.getGameTime()
                    self.node.miniBillboard2StartTime = t
                    self.node.miniBillboard2EndTime = t+gPowerupWearOffTime
                    self._bombWearOffFlashTimer = bs.Timer(gPowerupWearOffTime-2000,bs.WeakCall(self._bombWearOffFlash))
                    self._bombWearOffTimer = bs.Timer(gPowerupWearOffTime,bs.WeakCall(self._bombWearOff))
            elif msg.powerupType == 'electricBomb':
            	bsUtils.PopupText("Bomba Electrica",color=(0,0,0.6),scale=1.2,position=self.node.position).autoRetain()
                self.bombType = 'electric'
                tex = self._getBombTypeTex()
                self._flashBillboard(tex)
                if self.powerupsExpire:
                    self.node.miniBillboard2Texture = tex
                    t = bs.getGameTime()
                    self.node.miniBillboard2StartTime = t
                    self.node.miniBillboard2EndTime = t+gPowerupWearOffTime
                    self._bombWearOffFlashTimer = bs.Timer(gPowerupWearOffTime-2000,bs.WeakCall(self._bombWearOffFlash))
                    self._bombWearOffTimer = bs.Timer(gPowerupWearOffTime,bs.WeakCall(self._bombWearOff))
            elif msg.powerupType == 'power':
            	bsUtils.PopupText("Poder!",color=(1,0.2,0.2),scale=1.2,position=self.node.position).autoRetain()
                tex = bs.Powerup.getFactory().texPower
                self._flashBillboard(tex)
                self._punchPowerScale += 1
                #BlackHole(position = self.node.position)
                #MagneticZone(owner = self.node)
            elif msg.powerupType == 'knock':
                for p in bs.getActivity().players:
                    try:
                        if p.actor.isAlive():
                            p.actor.node.handleMessage('knockout',5000)
                    except Exception: bs.printException('Nothing changes')
            elif msg.powerupType == 'powerupBomb':
            	bsUtils.PopupText("Powerups???",color=(1,1,1),scale=1.2,position=self.node.position).autoRetain()
                self.setPowerupBombCount(min(self.powerupBombCount+4,4))
            elif msg.powerupType == 'speed':
            	bsUtils.PopupText("Velocidad",color=(0,1,0.3),scale=1.2,position=self.node.position).autoRetain()
                self.node.hockey = True
                tex = bs.Powerup.getFactory().texSpeed
                self._flashBillboard(tex)
                if self.powerupsExpire:                
                    self.node.miniBillboard2Texture = tex
                    t = bs.getGameTime()
                    self.node.miniBillboard2StartTime = t
                    self.node.miniBillboard2EndTime = t+gPowerupWearOffTime
                    self._speedWearOffFlashTimer = bs.Timer(gPowerupWearOffTime-2000,bs.WeakCall(self._speedWearOffFlash))
                    self._speedWearOffTimer = bs.Timer(gPowerupWearOffTime,bs.WeakCall(self._speedWearOff))
            elif (msg.powerupType == 'bombJumping'):
            	bsUtils.PopupText("Bomba Saltarina",color=(1,1,1),scale=1.2,position=self.node.position).autoRetain()
                self.bombType = 'saltarina'
                tex = self._getBombTypeTex()
                self._flashBillboard(tex)
                if self.powerupsExpire:
                    self.node.miniBillboard2Texture = tex
                    t = bs.getGameTime()
                    self.node.miniBillboard2StartTime = t
                    self.node.miniBillboard2EndTime = t+gPowerupWearOffTime
                    self._bombWearOffFlashTimer = bs.Timer(gPowerupWearOffTime-2000,bs.WeakCall(self._bombWearOffFlash))
                    self._bombWearOffTimer = bs.Timer(gPowerupWearOffTime,bs.WeakCall(self._bombWearOff))
            elif msg.powerupType == 'tntBombs':
            	bsUtils.PopupText("Bombas TNT",color=(0.7,0.7,0.5),scale=1.2,position=self.node.position).autoRetain()
                self.bombType = 'tntImpact'
                tex = self._getBombTypeTex()
                self._flashBillboard(tex)
                if self.powerupsExpire:
                    self.node.miniBillboard2Texture = tex
                    t = bs.getGameTime()
                    self.node.miniBillboard2StartTime = t
                    self.node.miniBillboard2EndTime = t+gPowerupWearOffTime
                    self._bombWearOffFlashTimer = bs.Timer(gPowerupWearOffTime-2000,bs.WeakCall(self._bombWearOffFlash))
                    self._bombWearOffTimer = bs.Timer(gPowerupWearOffTime,bs.WeakCall(self._bombWearOff))
            elif msg.powerupType == 'espectralBomb':
            	bsUtils.PopupText("Bomba Espectral",color=(2,2,2),scale=1.2,position=self.node.position).autoRetain()
                self.bombType = 'espectralBomb'
                tex = self._getBombTypeTex()
                self._flashBillboard(tex)
                if self.powerupsExpire:
                    self.node.miniBillboard2Texture = tex
                    t = bs.getGameTime()
                    self.node.miniBillboard2StartTime = t
                    self.node.miniBillboard2EndTime = t+gPowerupWearOffTime
                    self._bombWearOffFlashTimer = bs.Timer(gPowerupWearOffTime-2000,bs.WeakCall(self._bombWearOffFlash))
                    self._bombWearOffTimer = bs.Timer(gPowerupWearOffTime,bs.WeakCall(self._bombWearOff))                                        
            elif msg.powerupType == 'magicBomb':
            	bsUtils.PopupText("Orbe Magica",color=(0,0,0.4),scale=1.2,position=self.node.position).autoRetain()
                self.bombType = 'magicBomb'
                tex = self._getBombTypeTex()
                self._flashBillboard(tex)
                if self.powerupsExpire:
                    self.node.miniBillboard2Texture = tex
                    t = bs.getGameTime()
                    self.node.miniBillboard2StartTime = t
                    self.node.miniBillboard2EndTime = t+gPowerupWearOffTime
                    self._bombWearOffFlashTimer = bs.Timer(gPowerupWearOffTime-2000,bs.WeakCall(self._bombWearOffFlash))
                    self._bombWearOffTimer = bs.Timer(gPowerupWearOffTime,bs.WeakCall(self._bombWearOff))                                        
            elif msg.powerupType == 'iceImpact':
            	bsUtils.PopupText("Orbe Helada",color=(0,0.6,1),scale=1.2,position=self.node.position).autoRetain()
                self.bombType = 'iceImpact'
                tex = self._getBombTypeTex()
                self._flashBillboard(tex)
                if self.powerupsExpire:
                    self.node.miniBillboard2Texture = tex
                    t = bs.getGameTime()
                    self.node.miniBillboard2StartTime = t
                    self.node.miniBillboard2EndTime = t+gPowerupWearOffTime
                    self._bombWearOffFlashTimer = bs.Timer(gPowerupWearOffTime-2000,bs.WeakCall(self._bombWearOffFlash))
                    self._bombWearOffTimer = bs.Timer(gPowerupWearOffTime,bs.WeakCall(self._bombWearOff))                                        
            elif msg.powerupType == 'endBomb':
            	bsUtils.PopupText("Bomba del Fin",color=(1.3,0.2,0),scale=1.2,position=self.node.position).autoRetain()
                self.bombType = 'endBomb'
                tex = self._getBombTypeTex()
                self._flashBillboard(tex)
                if self.powerupsExpire:
                    self.node.miniBillboard2Texture = tex
                    t = bs.getGameTime()
                    self.node.miniBillboard2StartTime = t
                    self.node.miniBillboard2EndTime = t+gPowerupWearOffTime
                    self._bombWearOffFlashTimer = bs.Timer(gPowerupWearOffTime-2000,bs.WeakCall(self._bombWearOffFlash))
                    self._bombWearOffTimer = bs.Timer(gPowerupWearOffTime,bs.WeakCall(self._bombWearOff))
            elif msg.powerupType == 'bugBomb':
            	bsUtils.PopupText("Bomba Bug",color=(1,0.2,1*2),scale=1.2,position=self.node.position).autoRetain()
                self.bombType = 'bugBomb'
                tex = self._getBombTypeTex()
                self._flashBillboard(tex)
                if self.powerupsExpire:
                    self.node.miniBillboard2Texture = tex
                    t = bs.getGameTime()
                    self.node.miniBillboard2StartTime = t
                    self.node.miniBillboard2EndTime = t+gPowerupWearOffTime
                    self._bombWearOffFlashTimer = bs.Timer(gPowerupWearOffTime-2000,bs.WeakCall(self._bombWearOffFlash))
                    self._bombWearOffTimer = bs.Timer(gPowerupWearOffTime,bs.WeakCall(self._bombWearOff))
            elif msg.powerupType == 'eggBomb':
            	bsUtils.PopupText("Eggs",color=(1,0.2,1*2),scale=1.2,position=self.node.position).autoRetain()
                self.bombType = 'eggBomb'
                tex = self._getBombTypeTex()
                self._flashBillboard(tex)
                if self.powerupsExpire:
                    self.node.miniBillboard2Texture = tex
                    t = bs.getGameTime()
                    self.node.miniBillboard2StartTime = t
                    self.node.miniBillboard2EndTime = t+gPowerupWearOffTime
                    self._bombWearOffFlashTimer = bs.Timer(gPowerupWearOffTime-2000,bs.WeakCall(self._bombWearOffFlash))
                    self._bombWearOffTimer = bs.Timer(gPowerupWearOffTime,bs.WeakCall(self._bombWearOff))
            elif msg.powerupType == 'shockBomb':
            	bsUtils.PopupText("Bomba de Choque",color=(1,0.2,1*2),scale=1.2,position=self.node.position).autoRetain()
                self.bombType = 'shockBomb'
                tex = self._getBombTypeTex()
                self._flashBillboard(tex)
                if self.powerupsExpire:
                    self.node.miniBillboard2Texture = tex
                    t = bs.getGameTime()
                    self.node.miniBillboard2StartTime = t
                    self.node.miniBillboard2EndTime = t+gPowerupWearOffTime
                    self._bombWearOffFlashTimer = bs.Timer(gPowerupWearOffTime-2000,bs.WeakCall(self._bombWearOffFlash))
                    self._bombWearOffTimer = bs.Timer(gPowerupWearOffTime,bs.WeakCall(self._bombWearOff))
            elif msg.powerupType == 'dirigida':
            	bsUtils.PopupText("Bomba Dirigida",color=(0.8,2,0),scale=1.2,position=self.node.position).autoRetain()
                self.setDirigidaCount(min(self.dirigidaCount+2,2))
            elif msg.powerupType == 'cyp':    
            	bsUtils.PopupText("Eres un Suicida?",color=(1,1,1),scale=1.6,position=self.node.position).autoRetain()
                self.node.style = 'bones'
                self.node.headModel = bs.getModel('powerup')
                self.node.colorTexture = bs.getTexture('tnt')
                self.node.colorMaskTexture = bs.getTexture('bunnyColorMask')
                bs.animateArray(self.node,'color',3,{1000:(1,1,1),250:(1*2,0,0),1000:(1,1,1)},True)
                self.node.handleMessage('celebrate',10000)
                self.node.highlight = (1,0,0)
                self.bombType = 'tntImpact'
                self.setBombCount(10)
                self.curseTime=-1
                self.curse()
            elif msg.powerupType == 'palFire':    
                self.node.color = (1*2,0.6,0)
                self.node.highlight = (1*2,0.6,0)
                self.node.handleMessage('celebrate',10000)
            elif msg.powerupType == 'shock':
                self._colorRain = bs.Timer(100,bs.WeakCall(self.dropP),repeat = False)
                self._color1Rain = bs.Timer(300,bs.WeakCall(self.dropP),repeat = False)
                self._color2Rain = bs.Timer(500,bs.WeakCall(self.dropP),repeat = False)
                #self._color3Rain = bs.Timer(700,bs.WeakCall(self.dropP),repeat = False)
                #self._color4Rain = bs.Timer(900,bs.WeakCall(self.dropP),repeat = False)
            elif msg.powerupType == 'palMostro':
                self.node.style = random.choice(['bones','bear','pirate','female','spaz'])
                self.node.headModel = bs.getModel(random.choice(['powerup','impactBomb','bomb','puck','landMine','ninjaHand','box','flash','crossOut','egg']))
                self.node.colorTexture = bs.getTexture(random.choice(['powerupPunch','powerupShield','trophy','bonesColor','rgbStripes','multiplayerExamples','smoke']))
                self.node.colorMaskTexture = bs.getTexture('bunnyColorMask')
            elif msg.powerupType == 'BOSS':
            	self.node.style = 'bear'
                self.node.colorTexture = bs.getTexture('bearColor')
                self.node.colorMaskTexture = bs.getTexture('bearColorMask')
                self.node.headModel = bs.getModel('bearHead')
                self.node.torsoModel = bs.getModel('bearTorso')
                self.node.pelvisModel = bs.getModel('bearPelvis')
                self.node.upperArmModel = bs.getModel('bearUpperArm')
                self.node.foreArmModel = bs.getModel('bearForeArm')
                self.node.handModel = bs.getModel('bearHand')
                self.node.upperLegModel = bs.getModel('bearUpperLeg')
                self.node.lowerLegModel = bs.getModel('bearLowerLeg')
                self.node.toesModel = bs.getModel('bearToes')
                self.node.color = (0,0,0)
                self.node.highlight = (0,1,1)
                self.node.name = 'Oso maton'
                self.node.nameColor = (0.7,0.7,0.7)
                self.bombType = 'espectralBomb'
                self._colorRain = bs.Timer(1500,bs.WeakCall(self.bossTransition),repeat = False)
                self._bombRain = bs.Timer(2200,bs.WeakCall(self.bossInvocation),repeat = False)
                #bsUtils.animateArray(self.node,'color',3,{0: self._boss.node.color, 1000:(0,9,9),3000:self._boss.node.color})
            elif msg.powerupType == 'punch':
            	bsUtils.PopupText("Guantes de Boxeo",color=(1,0,0),scale=1.2,position=self.node.position).autoRetain()
                self._hasBoxingGloves = True
                tex = bs.Powerup.getFactory().texPunch
                self._flashBillboard(tex)
                self.equipBoxingGloves()
                if self.powerupsExpire:
                    self.node.boxingGlovesFlashing = 0
                    self.node.miniBillboard3Texture = tex
                    t = bs.getGameTime()
                    self.node.miniBillboard3StartTime = t
                    self.node.miniBillboard3EndTime = t+gPowerupWearOffTime
                    self._boxingGlovesWearOffFlashTimer = bs.Timer(gPowerupWearOffTime-2000,bs.WeakCall(self._glovesWearOffFlash))
                    self._boxingGlovesWearOffTimer = bs.Timer(gPowerupWearOffTime,bs.WeakCall(self._glovesWearOff))
            elif msg.powerupType == 'shield':
            	#bsUtils.PopupText("Escudo",color=(0.6,0,1),scale=1.2,position=self.node.position).autoRetain()
                factory = self.getFactory()
                # let's allow powerup-equipped shields to lose hp over time
                self.equipShields()
            elif msg.powerupType == 'shieldCoop':
            	#bsUtils.PopupText("Escudo",color=(0.6,0,1),scale=1.2,position=self.node.position).autoRetain()
                factory = self.getFactory()
                # let's allow powerup-equipped shields to lose hp over time
                self.equipShieldForBot()
            elif msg.powerupType == 'curse':
            	bsUtils.PopupText("Maldicion",color=(0,0,0.2),scale=1.2,position=self.node.position).autoRetain()
                self.curse()
            elif (msg.powerupType == 'iceBombs'):
            	bsUtils.PopupText("Bombas de Hielo",color=(0,0.2,1),scale=1.2,position=self.node.position).autoRetain()
                self.bombType = 'ice'
                tex = self._getBombTypeTex()
                self._flashBillboard(tex)
                if self.powerupsExpire:
                    self.node.miniBillboard2Texture = tex
                    t = bs.getGameTime()
                    self.node.miniBillboard2StartTime = t
                    self.node.miniBillboard2EndTime = t+gPowerupWearOffTime
                    self._bombWearOffFlashTimer = bs.Timer(gPowerupWearOffTime-2000,bs.WeakCall(self._bombWearOffFlash))
                    self._bombWearOffTimer = bs.Timer(gPowerupWearOffTime,bs.WeakCall(self._bombWearOff))
            elif msg.powerupType == 'god':
            	bsUtils.PopupText("Invencibilidad",color=(1,1,1),scale=1.2,position=self.node.position).autoRetain()
                self.node.invincible = True
                if self._cursed:
                    self._cursed = False
                    # remove cursed material
                    factory = self.getFactory()
                    for attr in ['materials','rollerMaterials']:
                        materials = getattr(self.node,attr)
                        if factory.curseMaterial in materials:
                            setattr(self.node,attr,tuple(m for m in materials if m != factory.curseMaterial))
                    self.node.curseDeathTime = 0
                tex = bs.Powerup.getFactory().texGod
                self._flashBillboard(tex)
                if self.powerupsExpire:
                    self.node.miniBillboard1Texture = tex
                    t = bs.getGameTime()
                    self.node.miniBillboard1StartTime = t
                    self.node.miniBillboard1EndTime = t+gPowerupWearOffTime-8000
                    self._godWearOffFlashTimer = bs.Timer(gPowerupWearOffTime-10000,bs.WeakCall(self._godWearOffFlash))
                    self._godWearOffTimer = bs.Timer(gPowerupWearOffTime-8000,bs.WeakCall(self._godWearOff))
            elif (msg.powerupType == 'extraLive'):
            	bsUtils.PopupText("Vida x2",color=(1.8,1,1),scale=1.2,position=self.node.position).autoRetain()
                if self._cursed:
                    self._cursed = False
                    # remove cursed material
                    factory = self.getFactory()
                    for attr in ['materials','rollerMaterials']:
                        materials = getattr(self.node,attr)
                        if factory.curseMaterial in materials:
                            setattr(self.node,attr,tuple(m for m in materials if m != factory.curseMaterial))
                    self.node.curseDeathTime = 0
                    bs.statAdd('Curse Cures')
                self.hitPoints = self.hitPointsMax = 2000
                self._flashBillboard(bs.Powerup.getFactory().texExtraLive)
                self.node.hurt = 0
                self._lastHitTime = None
                self._numTimesHit = 0
            elif (msg.powerupType == 'health'):
            	bsUtils.PopupText("Vida",color=(1.5,1,1),scale=1.2,position=self.node.position).autoRetain()
                if self._cursed:
                    self._cursed = False
                    # remove cursed material
                    factory = self.getFactory()
                    for attr in ['materials','rollerMaterials']:
                        materials = getattr(self.node,attr)
                        if factory.curseMaterial in materials:
                            setattr(self.node,attr,tuple(m for m in materials if m != factory.curseMaterial))
                    self.node.curseDeathTime = 0
                    bs.statAdd('Curse Cures')
                self.hitPoints = self.hitPointsMax
                self._flashBillboard(bs.Powerup.getFactory().texHealth)
                self.node.hurt = 0
                self._lastHitTime = None
                self._numTimesHit = 0
                
           ##############################LUCKY BLOCK#######################
            
            elif msg.powerupType == 'luckyBlock':
                    

                testingEvent = 0
                
                
                event = random.randint(1,41) if testingEvent == 0 else testingEvent
                print 'LuckyBlock event: ' + str(event)
                bs.statAdd('LuckyBlock collected')
                
                if event in [1,2,3,4,5]:
                    self.node.handleMessage(bs.PowerupMessage(powerupType = random.choice(['tripleBombs','iceBombs','punch','impactBombs','landMines','stickyBombs','shield'])))
                    
                elif event == 6:
                    print 'LuckyBlock taken. The effect: Powerups'
                    bsUtils.PopupText("powerups!",color=(1,1,1),scale=1.2,position=self.node.position).autoRetain()
                    bs.shakeCamera(1)
                    bs.emitBGDynamics(position=(self.node.position[0],self.node.position[1]+4,self.node.position[2]),velocity=(0,0,0),count=400,spread=0.7,chunkType='spark')
                    bs.Powerup(position=(self.node.position[0],self.node.position[1]+4,self.node.position[2]), powerupType=random.choice(["punch", "tripleBombs", "health", "iceBombs","impactBombs","curse"]), expire=True).autoRetain()
                    bs.Powerup(position=(self.node.position[0],self.node.position[1]+3,self.node.position[2]), powerupType=random.choice(["punch", "tripleBombs", "health", "iceBombs","impactBombs","landMine"]), expire=True).autoRetain()
                    
                elif event == 7:
                    print 'LuckyBlock taken. The effect: random effect'
                    bs.emitBGDynamics(position=self.node.position,velocity=(0,0,0),count=300,spread=0.7,chunkType=random.choice(['ice','rock','metal','spark','splinter','slime']));
                    bs.shakeCamera(0.5)
                    
                elif event == 8:
                    print 'LuckyBlock taken. The effect: Giant bomb'
                    bsUtils.PopupText("Mega Bomba :v",color=(0.4,0.2,0),scale=1.2,position=self.node.position).autoRetain()
                    bs.Bomb(position=(self.node.position[0],self.node.position[1]+2,self.node.position[2]),blastRadius=50.0,bombType=random.choice(['sticky','normal','ice','endBomb','landMine','powerupBomb','electric'])).autoRetain()
                    
                elif event == 9:
                    print 'LuckyBlock taken. The effect: Freeze'
                    bsUtils.PopupText("Congelado!",color=(0,0.6,1),scale=1.2,position=self.node.position).autoRetain()
                    self.node.handleMessage(bs.FreezeMessage())
                    
                elif event == 10:
                    print 'LuckyBlock taken. The effect: Punch blast'
                    bsUtils.PopupText("Lol",color=(1.5,1,1),scale=1.2,position=self.node.position).autoRetain()
                    bs.Blast(position=self.node.position, velocity=self.node.velocity, blastRadius=1.0, blastType='normal', sourcePlayer=None, hitType='punch', hitSubType='normal')
                    
                elif event == 11:
                    'LuckyBlock taken. The effect: 10 land-mines'
                    bsUtils.PopupText("Muchas Minas",color=(0,0.6,0.3),scale=1.2,position=self.node.position).autoRetain()
                    self.setLandMineCount(min(self.landMineCount+10,10))
                    
                elif event == 12:
                    print 'LuckyBlock taken. The effect: Freeze and kill'
                    bsUtils.PopupText("Mala Suerte",color=(0.8,0,0),scale=1.6,position=self.node.position).autoRetain()
                    bs.Blast(position=self.node.position, velocity=self.node.velocity, blastRadius=1.0, blastType='normal', sourcePlayer=None, hitType='punch', hitSubType='normal')
                    self.node.handleMessage(bs.FreezeMessage())
                    bs.Blast(position=self.node.position, velocity=self.node.velocity, blastRadius=1.0, blastType='normal', sourcePlayer=None, hitType='punch', hitSubType='normal')
                    self.node.handleMessage(bs.FreezeMessage())
                    bs.Blast(position=self.node.position, velocity=self.node.velocity, blastRadius=1.0, blastType='normal', sourcePlayer=None, hitType='punch', hitSubType='normal')
                
                elif event == 13:
                    print 'LuckyBlock taken. The effect: Random player color'
                    bsUtils.PopupText("Color",color=(0.7,0.7,0.7),scale=1.2,position=self.node.position).autoRetain()
                    self.node.color = (random.random()*2,random.random()*2,random.random()*2)
                    
                elif event == 14:
                    print 'LuckyBlock taken. The effect: Lighting'
                    bsUtils.PopupText("Luz XD",color=(1,1,1),scale=1.2,position=self.node.position).autoRetain()
                    light = bs.newNode('light',
                                    attrs={'position':(self.node.position),
                                        'color': (0.2,0.2,0.4),
                                        'volumeIntensityScale': 1.0,
                                        'radius':1})
                    bsUtils.animate(light,"intensity",{0:1,50:10,150:5,250:0,260:10,410:5,510:1})
                    self.node.connectAttr('positionCenter',light,'position')
                    
                elif event == 15:
                    print 'LuckyBlock taken. The effect: Giant bomb'
                    bs.Bomb(position=(self.node.position[0],self.node.position[1]+3,self.node.position[2]),blastRadius=2.0,bombType=random.choice(['magicBomb','espectralBomb','iceImpact','BdM','luckyBomb'])).autoRetain()
                    
                elif event == 16:
                    print 'LuckyBlock taken. The effect: Random models'
                    bsUtils.PopupText("Eres un Mago!",color=(1,1,1),scale=1.2,position=self.node.position).autoRetain()
                    self.bombType = random.choice(['magicBomb','iceImpact','BdM'])
                    self.node.style = 'spaz'
                    self.node.colorTexture = bs.getTexture('wizardColor')
                    self.node.colorMaskTexture = bs.getTexture('wizardColorMask')
                    self.node.headModel = bs.getModel('wizardHead')
                    self.node.torsoModel = bs.getModel('wizardTorso')
                    self.node.pelvisModel = bs.getModel('wizardPelvis')
                    self.node.upperArmModel = bs.getModel('wizardUpperArm')
                    self.node.foreArmModel = bs.getModel('wizardForeArm')
                    self.node.handModel = bs.getModel('wizardHand')
                    self.node.upperLegModel = bs.getModel('wizardUpperLeg')
                    self.node.lowerLegModel = bs.getModel('wizardLowerLeg')
                    self.node.toesModel = bs.getModel('wizardToes')
                    self.node.color = (random.random(),random.random(),random.random())
                    
                elif event == 17:
                    'LuckyBlock taken. The effect: 10 land-mines'
                    bsUtils.PopupText("Muchos powerups???",color=(1,1,1),scale=1.2,position=self.node.position).autoRetain()
                    self.setPowerupBombCount(min(self.powerupBombCount+8,8))
                    
                elif event == 18:
                    print 'LuckyBlock taken. The effect: Giant bomb'
                    bsUtils.PopupText("Atomic!!!",color=(1,1*2,0),scale=1.4,position=self.node.position).autoRetain()
                    bs.Bomb(position=(self.node.position[0],self.node.position[1]+3,self.node.position[2]),blastRadius=20.0,bombType=random.choice(['tnt'])).autoRetain()
                    
                elif event == 19:
                    print 'LuckyBlock taken. The effect: Stronger'
                    bsUtils.PopupText("Stonger",color=(1*3,0,0),scale=1.4,position=self.node.position).autoRetain()
                    self._punchPowerScale += 10
                    light = bs.newNode('light',
                                    attrs={'position':(self.node.position),
                                        'color': (1*3,0,0),
                                        'volumeIntensityScale': 0.4,
                                        'radius':0.1})
                    bsUtils.animate(light,"intensity",{0:1,50:10,150:5,250:0,260:10,410:5,510:0.3})
                    self.node.connectAttr('positionCenter',light,'position')
                    
                elif event == 20:
                    print 'LuckyBlock taken. The effect: Stronger'
                    bsUtils.PopupText("Vida x10!!!",color=(1*3,1*3,1*3),scale=1.4,position=self.node.position).autoRetain()
                    self.hitPoints = self.hitPointsMax = 10000
                    
                elif event == 21:
                    print 'LuckyBlock taken. The effect: Stronger'
                    bsUtils.PopupText("Super Escudo!!!",color=(1,1,0.5),scale=1.4,position=self.node.position).autoRetain()
                    self.equipShieldForBot()
                    self.shield.color = (1*2,1*2,1*2)
                    self.shieldHitPoints = self.shieldHitPointsMax = 5000
                    
                elif event == 22:
                    print 'LuckyBlock taken. The effect: Random models'
                    bsUtils.PopupText("Bomba de la Suerte!",color=(1,1,1),scale=1.2,position=self.node.position).autoRetain()
                    self.bombType = 'luckyBomb'
                    
                elif event == 23:
                    print 'LuckyBlock taken. The effect: Stronger'
                    bsUtils.PopupText("Esto es un Escudo??\nTen cuidado!\nEsto es muy raro\n:v",color=(1*3,1*3,1*3),scale=1.4,position=self.node.position).autoRetain()
                    self.equipShieldForBot()
                    self.shield1 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(random.random()*2,random.random()*2,random.random()*2),'radius':1.2})
                    self.node.connectAttr('positionCenter',self.shield1,'position')
                    self.shieldHitPoints = self.shieldHitPointsMax
                    bs.animate(self.shield1,'radius',{0:1.0,100:1.5,600:1.0},True)
                    
                elif event == 24:
                    print 'LuckyBlock taken. The effect: Stronger'
                    bsUtils.PopupText("Vas a Volar!\njajaja",color=(1,1*3,1),scale=1.4,position=self.node.position).autoRetain()
                    self.node.handleMessage(bs.FlyMessage())
                    
                elif event == 25:
                    print 'LuckyBlock taken. The effect: Stronger'
                    bsUtils.PopupText("Maldicion???",color=(0,0.1,0.2),scale=1.4,position=self.node.position).autoRetain()
                    self.node.curseDeathTime = bs.getGameTime()+120
                    
                elif event == 26:
                    print 'LuckyBlock taken. The effect: Stronger'
                    bsUtils.PopupText("Maldicion 2",color=(0,0.1,0.2),scale=1.4,position=self.node.position).autoRetain()
                    self.curse2()
                    
                elif event == 27:
                    print 'LuckyBlock taken. The effect: Stronger'
                    bsUtils.PopupText("Ups!\n:(\n:v\n;)",color=(0,0.1,0.2),scale=1.4,position=self.node.position).autoRetain()
                    bs.Spaz(character = random.choice(['B-9000','Bernard','Bones','Pascal','Pixel']),color = (random.random(),random.random(),random.random()),highlight = (random.random(),random.random(),random.random())).autoRetain().node.handleMessage(bs.StandMessage(position = self.node.position))
                    
                elif event == 28:
                    print 'LuckyBlock taken. The effect: Giant bomb'
                    bsUtils.PopupText("Hay Problemas!!!",color=(1,1,1),scale=1.2,position=self.node.position).autoRetain()
                    bs.Bomb(position=(self.node.position[0],self.node.position[1]+2,self.node.position[2]),blastRadius=0.3,bombType= 'crazyBomb').autoRetain()
                    
                elif event == 29:
                    print 'LuckyBlock taken. The effect: Freeze'
                    bsUtils.PopupText("Sorpresa!",color=(1,1,1),scale=1.2,position=(self.node.position[0],self.node.position[1]-0.5,self.node.position[2])).autoRetain()
                    bs.Blast(position=(self.node.position[0],self.node.position[1]+0.7,self.node.position[2]),velocity=(self.node.velocity[0],self.node.velocity[1],self.node.velocity[2]), blastRadius=0.1, blastType='endBomb', sourcePlayer=None, hitType='punch', hitSubType='punch')


                    
                elif event == 30:
                    print 'LuckyBlock taken. The effect: Freeze'
                    bsUtils.PopupText("Un Bot",color=(1,1,1),scale=1.2,position=self.node.position).autoRetain()
                    bs.getActivity()._botSet = bs.BotSet()
                    bs.getActivity()._botSet.spawnBot(ToughGuyBotProShielded,pos=self.node.position,spawnTime=5000)
                    
                elif event == 31:
                    print 'LuckyBlock taken. The effect: Freeze'
                    bsUtils.PopupText("Color al Mapa!",color=(1,1,1),scale=1.2,position=self.node.position).autoRetain()
                    #bs.playSound(bs.getSound('freeze'))
                    #self.iceMaterial = bs.Material()
                    #self.iceMaterial.addActions(actions=('modifyPartCollision','friction',0.06))
                    #bs.getActivity().getMap().node.materials = [bs.getSharedObject('footingMaterial'),self.iceMaterial]
                    bs.getActivity().getMap().node.color= (random.random()*2,random.random()*2,random.random()*2)
                    #bs.getActivity().getMap().node.reflection = 'soft'
                    #bs.getActivity().getMap().node.reflectionScale = [1]
                    
                    #bs.getActivity()._botSet = bs.BotSet()
                    #bs.getActivity()._botSet.spawnBot(FrostyBotPro,pos=self.node.position,spawnTime=1000)
                    #bs.getActivity()._botSet.spawnBot(PascalBot,pos=self.node.position,spawnTime=6000)
                   

                elif event == 32:
                    print 'LuckyBlock taken. The effect: Freeze'
                    bsUtils.PopupText("Maldicion T!",color=(1,1,1.5),scale=1.2,position=self.node.position).autoRetain()
                    #Portal(position1 = self.node.position,position2 = (self.node.position[0],self.node.position[1]+5,self.node.position[2]),color = (1*2,1*2,1*2))
                    #self.node.handleMessage(bs.StandMessage(position = (self.node.position[0],self.node.position[1]+5,self.node.position[2])))
                    self._colorRain = bs.Timer(500,bs.WeakCall(self.teleport),repeat = True)        
                    
                elif event == 33:
                    print 'LuckyBlock taken. The effect: Freeze'
                    bsUtils.PopupText("Colores!",color=(1,1,1),scale=1.2,position=self.node.position).autoRetain()
                    self._colorRain = bs.Timer(int(random.choice([100,150])),bs.WeakCall(self.colorGen),repeat = True)        
                    #self._text = bs.Timer(94000,bs.WeakCall(self.text))
                    
                elif event == 34:
                    print 'LuckyBlock taken. The effect: Punch wave'
                    bsUtils.PopupText("Oleada de golpes!",color=(1,0,0),scale=1.4,position=self.node.position).autoRetain()
                    wwwx = self.node.position[0]-2
                    while wwwx < self.node.position[0]+2:
                        wwwy = self.node.position[2]-2
                        while wwwy < self.node.position[2]+2:
                            bs.Blast(position=(wwwx,self.node.position[1],wwwy),velocity=(self.node.velocity[0],self.node.velocity[1]+10,self.node.velocity[2]), blastRadius=0.5, blastType='normal', sourcePlayer=None, hitType='punch', hitSubType='normal')
                            wwwy +=1
                        wwwx +=1
                        
                elif event == 35:
                    print 'LuckyBlock taken. The effect: Punch wave'
                    bsUtils.PopupText("Es Oso maton!!!",color=(0,0.4,0.7),scale=1.4,position=self.node.position).autoRetain()
                    self._spazArray = []
                    s = bs.Spaz(character = 'Bernard',color = (0,0,0),highlight =(0,1,1))
                    s.node.name = "Oso maton"
                    s.node.nameColor = (1,1,1)
                    s.hitPoints = 30000
                    s.node.handleMessage(bs.StandMessage(position = (random.randint(-4,4),3,random.randint(-7,1)),angle = int(random.random()*360)))
                    s.node.handleMessage('celebrate',5430000)
                    self._spazArray.append(s)
                    
                    bs.Bomb(position=(self.node.position[0],self.node.position[1]+2,self.node.position[2]),blastRadius=20.0,bombType=random.choice(['powerupBomb'])).autoRetain()
                    
                elif event == 36:
                    print 'LuckyBlock taken. The effect: Punch wave'
                    bsUtils.PopupText("Un agujero Negro!!!",color=(1.2,1,1),scale=1.3,position=self.node.position).autoRetain()
                    BlackHole(position = self.node.position)
                    
                elif event == 37:
                    print 'LuckyBlock taken. The effect: Punch wave'
                    bsUtils.PopupText("Eres un iman!!!",color=(0.8,0.8,1),scale=1.2,position=self.node.position).autoRetain()
                    MagneticZone(owner = self.node)
                    
                elif event == 38:
                    print 'LuckyBlock taken. The effect: Punch wave'
                    bsUtils.PopupText("Ha llegado la artilleria",color=(1,0.5,0),scale=1.2,position=self.node.position).autoRetain()
                    Artillery(position = self.node.position,owner = self.node,sourcePlayer = self.getPlayer())
                    
                elif event == 39:
                    print 'LuckyBlock taken. The effect: Punch wave'
                    bsUtils.PopupText("Oleada de Choques\npor 5s",color=(1,0.2,0.2),scale=1.2,position=self.node.position).autoRetain()
                    self._colorRain = bs.Timer(1000,bs.WeakCall(self.dropP),repeat = False)
                    self._color1Rain = bs.Timer(2000,bs.WeakCall(self.dropP),repeat = False)
                    self._color2Rain = bs.Timer(3000,bs.WeakCall(self.dropP),repeat = False)
                    self._color3Rain = bs.Timer(4000,bs.WeakCall(self.dropP),repeat = False)
                    self._color4Rain = bs.Timer(5000,bs.WeakCall(self.dropP),repeat = False)
                                      
                elif event == 40:
                    print 'LuckyBlock taken. The effect: Punch wave'
                    bsUtils.PopupText("A dar Vueltas",color=(1,0.9,0.6),scale=1.2,position=self.node.position).autoRetain()
                    self._baile = bs.Timer(260,bs.WeakCall(self._Move),repeat=False)
                    self._off = bs.Timer(160,bs.WeakCall(self.disconnect),repeat=False)
                    self._on = bs.Timer(2500,bs.WeakCall(self.connect),repeat=False)
                    self.node.handleMessage('celebrate',2000)
                    #bsUtils.animateArray(self.node,'color',3,{0: self.node.color, 800:(random.random()*2,random.random()*2,random.random()*2),2000:self.node.color})
                    #bsUtils.animateArray(self.node,'color',3,{0: self.node.color, 250:(self.node.color[0]*9,self.node.color[1]*9,self.node.color[2]*9),500:self.node.color,750:self.node.color},True)
                   
                elif event == 41:
                    print 'LuckyBlock taken. The effect: Punch wave'
                    bsUtils.PopupText("A mover el bote xd",color=(1,0.9,0.6),scale=1.2,position=self.node.position).autoRetain()
                    #self._baile = bs.Timer(100,bs.WeakCall(self._Move),repeat=False)
                    self.node.handleMessage('celebrate',2000)
                    self._move1 = bs.Timer(260,bs.WeakCall(self._Move2),repeat=False)
                    self._off = bs.Timer(160,bs.WeakCall(self.disconnect),repeat=False)
                    self._on = bs.Timer(2500,bs.WeakCall(self.connect),repeat=False)
                    
                    
           ##############################LUCKY BLOCK#######################
            
            elif msg.powerupType == 'powerupsLol':
                    

                testingEvent = 0
                
                
                event = random.randint(1,5) if testingEvent == 0 else testingEvent
                print 'LuckyBlock event: ' + str(event)
                
                if event in [1,2]:
                    self.node.handleMessage(bs.PowerupMessage(powerupType = random.choice(['shield','speed','god'])))
                    
                elif event == 3:
                    print 'LuckyBlock taken. The effect: Powerups'
                    bsUtils.PopupText("Super Stonger",color=(1*3,0,0),scale=1.4,position=self.node.position).autoRetain()
                    self._punchPowerScale = 20
                    light = bs.newNode('light',
                                    attrs={'position':(self.node.position),
                                        'color': (1*3,0,0),
                                        'volumeIntensityScale': 0.4,
                                        'radius':0.1})
                    bsUtils.animate(light,"intensity",{0:1,50:10,150:5,250:0,260:10,410:5,510:0.3})
                    bs.playSound(bs.getSound('grom2'))
                    self.node.connectAttr('positionCenter',light,'position')
                    
                elif event == 4:
                    print 'LuckyBlock taken. The effect: random effect'
                    bsUtils.PopupText("Super Mega Escudo!!!",color=(0,0.2,1*2),scale=1.4,position=self.node.position).autoRetain()
                    self.equipShieldForBot()
                    self.shield.color = (0,0,1*4)
                    self.shieldHitPoints = self.shieldHitPointsMax = 8000
                    
                elif event == 5:
                    print 'LuckyBlock taken. The effect: Giant bomb'
                    bsUtils.PopupText("Vida x15!!!",color=(1*3,1*3,1*3),scale=1.4,position=self.node.position).autoRetain()
                    self.hitPoints = self.hitPointsMax = 15000
                
            self.node.handleMessage("flash")
            if msg.sourceNode.exists():
                msg.sourceNode.handleMessage(bs.PowerupAcceptMessage())
            return True

        elif isinstance(msg, bs.FreezeMessage):
            if not self.node.exists(): return
            if self.node.invincible == True:
                bs.playSound(self.getFactory().blockSound, 1.0,
                             position=self.node.position)
                return
            if self.shield is not None: return
            if not self.frozen:
                self.frozen = True
                self.node.frozen = 1
                bs.gameTimer(5000, bs.WeakCall(self.handleMessage,
                                               bs.ThawMessage()))
                # instantly shatter if we're already dead
                # (otherwise its hard to tell we're dead)
                if self.hitPoints <= 0:
                    self.shatter()

        elif isinstance(msg, bs.ThawMessage):
            if self.frozen and not self.shattered and self.node.exists():
                self.frozen = False
                self.node.frozen = 0
                bs.statAdd('Ice Thawed')
                
        elif isinstance(msg,bs.ElectricMessage):
        	if not self.node.exists(): return
        	if self.node.invincible == True:
        		return
        	if self.shield is not None: return
        	self.alto = True
        	def normal():
        		self.alto = False
        	bs.gameTimer(12000,bs.Call(normal))
        
        elif isinstance(msg,bs.EspectralMessage):
        	#if not self.node.exists(): return
        	#if self.node.invincible == True:
        		#return
        	#if self.shield is not None: return
        	self.node.color = (self.node.color[0]*7,self.node.color[1]*7,self.node.color[2]*7)
        	bs.gameTimer(2000, bs.WeakCall(self.handleMessage,
                                               bs.DieMessage()))

        elif isinstance(msg,bs.BugMessage):
        	if not self.node.exists(): return
        	if self.node.invincible == True:
        		return
        	if self.shield is not None: return
        	self._color = bs.Timer(100,bs.WeakCall(self._bug),repeat=True)
        	def normal():
        		self._color = bs.Timer(100,bs.WeakCall(self._offBug),repeat=False)
        	bs.gameTimer(12000,bs.Call(normal))
        
        elif isinstance(msg,bs.FlyMessage):
        	#if not self.node.exists(): return
        	#if self.node.invincible == True:
        		#return
        	#if self.shield is not None: return
        	self.node.fly = True
        	def normal():
        		self.node.fly = False
        	bs.gameTimer(15000,bs.Call(normal))
                
        elif isinstance(msg, bs.HitMessage):
            if not self.node.exists(): return
            if self.node.invincible == True:
                bs.playSound(self.getFactory().blockSound,
                             1.0, position=self.node.position)
                return True

            # if we were recently hit, don't count this as another
            # (so punch flurries and bomb pileups essentially count as 1 hit)
            gameTime = bs.getGameTime()
            if self._lastHitTime is None or gameTime-self._lastHitTime > 1000:
                self._numTimesHit += 1
                self._lastHitTime = gameTime
            
            mag = msg.magnitude * self._impactScale
            velocityMag = msg.velocityMagnitude * self._impactScale

            damageScale = 0.22
                
            if msg.hitSubType == 'mostro':
                damageScale = 0.1
                
            if msg.hitSubType == 'iceImpact':
                damageScale = 0.2
                
            if msg.hitSubType == 'endBomb':
                damageScale = 0
                
            if msg.hitSubType == 'BdM':
                damageScale = 0
                
            if msg.hitSubType == 'BdV':
                damageScale = 0
                
            if msg.hitSubType == 'tntImpact':
                damageScale = 0.35
                
            if msg.hitSubType == 'shockBomb':
                damageScale = 0.06

            # if they've got a shield, deliver it to that instead..
            if self.shield is not None:

                if msg.flatDamage: damage = msg.flatDamage * self._impactScale
                else:
                    # hit our spaz with an impulse but tell it to only return
                    # theoretical damage; not apply the impulse..
                    self.node.handleMessage(
                        "impulse", msg.pos[0], msg.pos[1], msg.pos[2],
                        msg.velocity[0], msg.velocity[1], msg.velocity[2],
                        mag , velocityMag, msg.radius, 1,
                        msg.forceDirection[0], msg.forceDirection[1],
                        msg.forceDirection[2])
                    damage = damageScale * self.node.damage

                self.shieldHitPoints -= damage

                self.shield.hurt = (1.0 - float(self.shieldHitPoints)
                                    /self.shieldHitPointsMax)
                # its a cleaner event if a hit just kills the shield
                # without damaging the player..
                # however, massive damage events should still be able to
                # damage the player.. this hopefully gives us a happy medium.
                maxSpillover = self.getFactory().maxShieldSpilloverDamage
                if self.shieldHitPoints <= 0:
                    # fixme - transition out perhaps?..
                    self.shield.delete()
                    self.shield = None
                    bs.playSound(self.getFactory().shieldDownSound, 1.0,
                                 position=self.node.position)
                    # emit some cool lookin sparks when the shield dies
                    t = self.node.position
                    bs.emitBGDynamics(position=(t[0], t[1]+0.9, t[2]),
                                      velocity=self.node.velocity,
                                      count=random.randrange(20, 30), scale=1.0,
                                      spread=0.6, chunkType='spark')

                else:
                    bs.playSound(self.getFactory().shieldHitSound, 0.5,
                                 position=self.node.position)

                # emit some cool lookin sparks on shield hit
                bs.emitBGDynamics(position=msg.pos,
                                  velocity=(msg.forceDirection[0]*1.0,
                                            msg.forceDirection[1]*1.0,
                                            msg.forceDirection[2]*1.0),
                                  count=min(30, 5+int(damage*0.005)),
                                  scale=0.5, spread=0.3, chunkType='spark')

                # if they passed our spillover threshold,
                # pass damage along to spaz
                if self.shieldHitPoints <= -maxSpillover:
                    leftoverDamage = -maxSpillover-self.shieldHitPoints
                    shieldLeftoverRatio = leftoverDamage/damage

                    # scale down the magnitudes applied to spaz accordingly..
                    mag *= shieldLeftoverRatio
                    velocityMag *= shieldLeftoverRatio
                else:
                    return True # good job shield!
            else: shieldLeftoverRatio = 1.0

            if msg.flatDamage:
                damage = (msg.flatDamage * self._impactScale
                          * shieldLeftoverRatio)
            else:
                # hit it with an impulse and get the resulting damage
                self.node.handleMessage(
                    "impulse", msg.pos[0], msg.pos[1], msg.pos[2],
                    msg.velocity[0], msg.velocity[1], msg.velocity[2],
                    mag, velocityMag, msg.radius, 0,
                    msg.forceDirection[0], msg.forceDirection[1],
                    msg.forceDirection[2])

                damage = damageScale * self.node.damage
            self.node.handleMessage("hurtSound")

            # play punch impact sound based on damage if it was a punch
            if msg.hitType == 'punch':

                self.onPunched(damage)

                if damage > 999:
                    bs.statAdd('CRIT Count')
                    bsUtils.PopupText("FATALITY!!!",color=(1,0,0),scale=1.4,position=self.node.position).autoRetain()
                    self.light = bs.newNode('light',
                           attrs={'position':self.node.position,
                                  'color': (1,0,0),
                                  'radius':1.0,
                                  'volumeIntensityScale': 1.0}) 
                    bs.animate(self.light,'intensity',{0:0,250:4.0,750:0},loop=False)
                    bs.gameTimer(750,self.light.delete)  
                    
                elif damage > 800 and damage < 999:
                    bsUtils.PopupText("CRAZY!!!",color=(1,1,0),scale=1.4,position=self.node.position).autoRetain()
                    
                elif damage > 730 and damage < 800:
                    bsUtils.PopupText("AGRESSIVE!!!",color=(0,1,0),scale=1.4,position=self.node.position).autoRetain()
                    
                elif damage > 10 and damage < 300:
                    bsUtils.PopupText(":v",color=(0,0,0),scale=0.8,position=self.node.position).autoRetain()

                # if damage was significant, lets show it
                if damage > 350:
                    bsUtils.showDamageCount('-' + str(int(damage/10)) + "%",
                                            msg.pos, msg.forceDirection)
                                               
                # lets always add in a super-punch sound with boxing
                # gloves just to differentiate them
                if msg.hitSubType == 'superPunch':
                    bs.playSound(self.getFactory().punchSoundStronger, 1.0,
                                 position=self.node.position)
                if damage > 500:
                    sounds = self.getFactory().punchSoundsStrong
                    sound = sounds[random.randrange(len(sounds))]
                else: sound = self.getFactory().punchSound
                bs.playSound(sound, 1.0, position=self.node.position)

                # throw up some chunks
                bs.emitBGDynamics(position=msg.pos,
                                  velocity=(msg.forceDirection[0]*0.5,
                                            msg.forceDirection[1]*0.5,
                                            msg.forceDirection[2]*0.5),
                                  count=min(10, 1+int(damage*0.0025)),
                                  scale=0.3, spread=0.03);

                bs.emitBGDynamics(position=msg.pos,
                                  chunkType='sweat',
                                  velocity=(msg.forceDirection[0]*1.3,
                                            msg.forceDirection[1]*1.3+5.0,
                                            msg.forceDirection[2]*1.3),
                                  count=min(30, 1+int(damage*0.04)),
                                  scale=0.9,
                                  spread=0.28);
                # momentary flash
                hurtiness = damage*0.003
                punchPos = (msg.pos[0]+msg.forceDirection[0]*0.02,
                            msg.pos[1]+msg.forceDirection[1]*0.02,
                            msg.pos[2]+msg.forceDirection[2]*0.02)
                flashColor = (1.0, 0.8, 0.4)
                light = bs.newNode("light",
                                   attrs={'position':punchPos,
                                          'radius':0.12+hurtiness*0.12,
                                          'intensity':0.3*(1.0+1.0*hurtiness),
                                          'heightAttenuated':False,
                                          'color':flashColor})
                bs.gameTimer(60, light.delete)


                flash = bs.newNode("flash",
                                   attrs={'position':punchPos,
                                          'size':0.17+0.17*hurtiness,
                                          'color':flashColor})
                bs.gameTimer(60, flash.delete)

            if msg.hitType == 'impact':
                bs.emitBGDynamics(position=msg.pos,
                                  velocity=(msg.forceDirection[0]*2.0,
                                            msg.forceDirection[1]*2.0,
                                            msg.forceDirection[2]*2.0),
                                  count=min(10, 1+int(damage*0.01)),
                                  scale=0.4, spread=0.1);
            if self.hitPoints > 0:
                # its kinda crappy to die from impacts, so lets reduce
                # impact damage by a reasonable amount if it'll keep us alive
                if msg.hitType == 'impact' and damage > self.hitPoints:
                    # drop damage to whatever puts us at 10 hit points,
                    # or 200 less than it used to be whichever is greater
                    # (so it *can* still kill us if its high enough)
                    newDamage = max(damage-200, self.hitPoints-10)
                    damage = newDamage
                self.node.handleMessage("flash")
                # if we're holding something, drop it
                if damage > 0.0 and self.node.holdNode.exists():
                    self.node.holdNode = bs.Node(None)
                self.hitPoints -= damage
                self.node.hurt = 1.0 - float(self.hitPoints)/self.hitPointsMax
                # if we're cursed, *any* damage blows us up
                if self._cursed and damage > 0:
                    bs.gameTimer(50, bs.WeakCall(self.curseExplode,
                                                 msg.sourcePlayer))
                # if we're frozen, shatter.. otherwise die if we hit zero
                if self.frozen and (damage > 200 or self.hitPoints <= 0):
                    self.shatter()
                elif self.hitPoints <= 0:
                    self.node.handleMessage(bs.DieMessage(how='impact'))

            # if we're dead, take a look at the smoothed damage val
            # (which gives us a smoothed average of recent damage) and shatter
            # us if its grown high enough
            if self.hitPoints <= 0:
                damageAvg = self.node.damageSmoothed * damageScale
                if damageAvg > 1000:
                    self.shatter()

        elif isinstance(msg, _BombDiedMessage):
            self.bombCount += 1
        
        elif isinstance(msg, bs.DieMessage):
            wasDead = self._dead
            self._dead = True
            self.hitPoints = 0
            if msg.immediate:
                self.node.delete()
            elif self.node.exists():
                self.node.hurt = 1.0
                if self.playBigDeathSound and not wasDead:
                    bs.playSound(self.getFactory().singlePlayerDeathSound)
                self.node.dead = True
                bs.gameTimer(2000, self.node.delete)

        elif isinstance(msg, bs.OutOfBoundsMessage):
            # by default we just die here
            self.handleMessage(bs.DieMessage(how='fall'))
        elif isinstance(msg, bs.StandMessage):
            self._lastStandPos = (msg.position[0], msg.position[1],
                                  msg.position[2])
            self.node.handleMessage("stand", msg.position[0], msg.position[1],
                                    msg.position[2], msg.angle)
        elif isinstance(msg, _CurseExplodeMessage):
            self.curseExplode()
        elif isinstance(msg, _PunchHitMessage):
            node = bs.getCollisionInfo("opposingNode")

            # only allow one hit per node per punch
            if (node is not None and node.exists()
                and not node in self._punchedNodes):
                
                punchMomentumAngular = (self.node.punchMomentumAngular
                                        * self._punchPowerScale)
                punchPower = self.node.punchPower * self._punchPowerScale

                # ok here's the deal:  we pass along our base velocity for use
                # in the impulse damage calculations since that is a more
                # predictable value than our fist velocity, which is rather
                # erratic. ...however we want to actually apply force in the
                # direction our fist is moving so it looks better.. so we still
                # pass that along as a direction ..perhaps a time-averaged
                # fist-velocity would work too?.. should try that.
                
                # if its something besides another spaz, just do a muffled punch
                # sound
                if node.getNodeType() != 'spaz':
                    sounds = self.getFactory().impactSoundsMedium
                    sound = sounds[random.randrange(len(sounds))]
                    bs.playSound(sound, 1.0, position=self.node.position)

                t = self.node.punchPosition
                punchDir = self.node.punchVelocity
                v = self.node.punchMomentumLinear

                self._punchedNodes.add(node)
                node.handleMessage(
                    bs.HitMessage(
                        pos=t,
                        velocity=v,
                        magnitude=punchPower*punchMomentumAngular*110.0,
                        velocityMagnitude=punchPower*40,
                        radius=0,
                        srcNode=self.node,
                        sourcePlayer=self.sourcePlayer,
                        forceDirection = punchDir,
                        hitType='punch',
                        hitSubType=('superPunch' if self._hasBoxingGloves
                                    else 'default')))

                # also apply opposite to ourself for the first punch only
                # ..this is given as a constant force so that it is more
                # noticable for slower punches where it matters.. for fast
                # awesome looking punches its ok if we punch 'through'
                # the target
                mag = -400.0
                if self._hockey: mag *= 0.5
                if len(self._punchedNodes) == 1:
                    self.node.handleMessage("kickBack", t[0], t[1], t[2],
                                            punchDir[0], punchDir[1],
                                            punchDir[2], mag)

        elif isinstance(msg, _PickupMessage):
            opposingNode, opposingBody = bs.getCollisionInfo('opposingNode',
                                                            'opposingBody')

            if opposingNode is None or not opposingNode.exists(): return True

            # dont allow picking up of invincible dudes
            try:
                if opposingNode.invincible == True: return True
            except Exception: pass

            # if we're grabbing the pelvis of a non-shattered spaz, we wanna
            # grab the torso instead
            if (opposingNode.getNodeType() == 'spaz'
                and not opposingNode.shattered and opposingBody == 4):
                opposingBody = 1

            # special case - if we're holding a flag, dont replace it
            # ( hmm - should make this customizable or more low level )
            held = self.node.holdNode
            if (held is not None and held.exists()
                and held.getNodeType() == 'flag'): return True
            self.node.holdBody = opposingBody # needs to be set before holdNode
            self.node.holdNode = opposingNode
        else:
            bs.Actor.handleMessage(self, msg)
            
    def dropM(self):
        bs.getActivity().mBotSet.spawnBot(bs.ToughGuyBotLame, pos=(-7.3+15.3*random.random(),8,(random.random()*14)-7),spawnTime = 0)
        
    def dropB(self):
        pos = (-7.3+15.3*random.random(),6,-5.5+2.1*random.random())
        vel = ((-5.0+random.random()*30.0) * (-1.0 if pos[0] > 0 else 1.0), -4.0,random.uniform(-20,20))
        bs.Bomb(position=pos,velocity=vel,bombType = 'impact').autoRetain()
        
        
    def dropP(self):
    	ShockWave(position = (self.node.position[0],self.node.position[1]-0.5,self.node.position[2]))
        #pos = (-7.3+15.3*random.random(),6,-5.5+(14*random.random()))
        #bs.Powerup(position = pos, powerupType = random.choice(['tripleBombs','punch','iceBombs','health','shield','stickyBombs','impactBombs','curse','landMines','luckyBlock','extraAccelerator'])).autoRetain()
        
    def soulExtractor(self):
        if self.node.exists():
            bs.emitBGDynamics(position=self.node.position,velocity=(0,18,0),count=100,spread=0.1,scale = 0.6,chunkType='spark')
            self.node.color = (self.node.color[0]-0.005,self.node.color[1]-0.005,self.node.color[2]-0.005)
            if self.node.color < (0,0,0):
                self.curse()
        else:
            self._soulSucker = None
            
    def colorGen(self):
        if self.node.exists():self.node.color = (random.random()*2,random.random()*2,random.random()*2)
        
    def teleport(self):
        self.node.handleMessage(bs.StandMessage(position = (self.node.position[0],self.node.position[1]-0.9,self.node.position[2])))
        #self.node.handleMessage(bs.StandMessage(position = (-0.5+1*random.random(),2,-0.5+1*random.random())))
        
    def bossTransition(self):
        bsUtils.animateArray(self.node,'color',3,{0: self.node.color, 1000:(0,9,9),3000:self.node.color})
        
    def bossInvocation(self):
        bs.Bomb(position=(self.node.position[0]+3,self.node.position[1]+2,self.node.position[2]),blastRadius=1,bombType='espectralBomb').autoRetain()
        bs.Bomb(position=(self.node.position[0]-3,self.node.position[1]+2,self.node.position[2]),blastRadius=1,bombType='espectralBomb').autoRetain()
        bs.Bomb(position=(self.node.position[0],self.node.position[1]+2,self.node.position[2]+3),blastRadius=1,bombType='espectralBomb').autoRetain()
        bs.Bomb(position=(self.node.position[0],self.node.position[1]+2,self.node.position[2]-3),blastRadius=1,bombType='espectralBomb').autoRetain()
        bs.Bomb(position=(self.node.position[0]+3,self.node.position[1]+2,self.node.position[2]+3),blastRadius=1,bombType='espectralBomb').autoRetain()
        bs.Bomb(position=(self.node.position[0]-3,self.node.position[1]+2,self.node.position[2]-3),blastRadius=1,bombType='espectralBomb').autoRetain()
        bs.Bomb(position=(self.node.position[0]+3,self.node.position[1]+2,self.node.position[2]-3),blastRadius=1,bombType='espectralBomb').autoRetain()
        bs.Bomb(position=(self.node.position[0]-3,self.node.position[1]+2,self.node.position[2]+3),blastRadius=1,bombType='espectralBomb').autoRetain()
               
    def connect(self): 
        self.connectControlsToPlayer()
       
    def disconnect(self): 
    	self.disconnectControlsFromPlayer()
                   
    def _jump(self): 
        #self.onJumpPress()
        self.node.jumpPressed = True
        self.node.jumpPressed = False
       
    def _Up(self):
    	self.node.moveUpDown = 1
        
    def _Down(self):
    	self.node.moveUpDown = -1
        
    def _Left(self):
        self.node.moveLeftRight = 1
        
    def _Right(self):
        self.node.moveLeftRight = -1
                        
    def _stop(self):
        self.node.moveLeftRight = 0
        self.node.moveUpDown = 0

    def _Move(self):
    	self._move1 = bs.Timer(60,bs.WeakCall(self._Up),repeat=False)
        self._move2 = bs.Timer(120,bs.WeakCall(self._Left),repeat=False)
        self._move3 = bs.Timer(180,bs.WeakCall(self._Down),repeat=False)
        self._move4 = bs.Timer(240,bs.WeakCall(self._Right),repeat=False)
        self._move5 = bs.Timer(300,bs.WeakCall(self._Up),repeat=False)
        self._move6 = bs.Timer(360,bs.WeakCall(self._Left),repeat=False)
        self._move7 = bs.Timer(420,bs.WeakCall(self._Down),repeat=False)
        self._move8 = bs.Timer(480,bs.WeakCall(self._Right),repeat=False)
        self._move9 = bs.Timer(540,bs.WeakCall(self._Up),repeat=False)
        self._move10 = bs.Timer(600,bs.WeakCall(self._Left),repeat=False)
        self._move11 = bs.Timer(660,bs.WeakCall(self._Down),repeat=False)
        self._move12 = bs.Timer(720,bs.WeakCall(self._Right),repeat=False)
        self._move13 = bs.Timer(780,bs.WeakCall(self._Up),repeat=False)
        self._move14 = bs.Timer(840,bs.WeakCall(self._Left),repeat=False)
        self._move15 = bs.Timer(900,bs.WeakCall(self._Down),repeat=False)
        self._move16 = bs.Timer(960,bs.WeakCall(self._Right),repeat=False)
        self._move17 = bs.Timer(1020,bs.WeakCall(self._Up),repeat=False)
        self._move18 = bs.Timer(1080,bs.WeakCall(self._Left),repeat=False)
        self._move19 = bs.Timer(1140,bs.WeakCall(self._Down),repeat=False)
        self._move20 = bs.Timer(1200,bs.WeakCall(self._Right),repeat=False)
        self._move21 = bs.Timer(1260,bs.WeakCall(self._Up),repeat=False)
        self._move22 = bs.Timer(1320,bs.WeakCall(self._Left),repeat=False)
        self._move23 = bs.Timer(1380,bs.WeakCall(self._Down),repeat=False)
        self._move24 = bs.Timer(1440,bs.WeakCall(self._Right),repeat=False)
        self._move25 = bs.Timer(2940,bs.WeakCall(self._stop),repeat=False)

    def _Move2(self):
    	self._move1 = bs.Timer(60,bs.WeakCall(self._Down),repeat=False)
        self._move2 = bs.Timer(120,bs.WeakCall(self._Left),repeat=False)
        self._move3 = bs.Timer(180,bs.WeakCall(self._Right),repeat=False)
        self._move4 = bs.Timer(240,bs.WeakCall(self._Left),repeat=False)
        self._move5 = bs.Timer(300,bs.WeakCall(self._Right),repeat=False)
        self._move6 = bs.Timer(360,bs.WeakCall(self._Left),repeat=False)
        self._move7 = bs.Timer(420,bs.WeakCall(self._Right),repeat=False)
        self._move8 = bs.Timer(480,bs.WeakCall(self._Left),repeat=False)
        self._move9 = bs.Timer(540,bs.WeakCall(self._Right),repeat=False)
        self._move10 = bs.Timer(600,bs.WeakCall(self._Left),repeat=False)
        self._move11 = bs.Timer(660,bs.WeakCall(self._Right),repeat=False)
        self._move12 = bs.Timer(720,bs.WeakCall(self._Left),repeat=False)
        self._move13 = bs.Timer(780,bs.WeakCall(self._Right),repeat=False)
        self._move14 = bs.Timer(840,bs.WeakCall(self._Left),repeat=False)
        self._move15 = bs.Timer(900,bs.WeakCall(self._Right),repeat=False)
        self._move16 = bs.Timer(960,bs.WeakCall(self._Left),repeat=False)
        self._move17 = bs.Timer(1020,bs.WeakCall(self._Right),repeat=False)
        self._move18 = bs.Timer(1080,bs.WeakCall(self._Left),repeat=False)
        self._move19 = bs.Timer(1140,bs.WeakCall(self._Right),repeat=False)
        self._move20 = bs.Timer(1200,bs.WeakCall(self._Left),repeat=False)
        self._move21 = bs.Timer(1260,bs.WeakCall(self._Right),repeat=False)
        self._move22 = bs.Timer(1320,bs.WeakCall(self._Left),repeat=False)
        self._move23 = bs.Timer(1380,bs.WeakCall(self._Right),repeat=False)
        self._move24 = bs.Timer(1440,bs.WeakCall(self._Left),repeat=False)
        self._move_1 = bs.Timer(1500,bs.WeakCall(self._jump),repeat=False)
        self._move_2 = bs.Timer(1560,bs.WeakCall(self._Left),repeat=False)
        self._move_3 = bs.Timer(1620,bs.WeakCall(self._Right),repeat=False)
        self._move_4 = bs.Timer(1680,bs.WeakCall(self._Left),repeat=False)
        self._move_5 = bs.Timer(1740,bs.WeakCall(self._Right),repeat=False)
        self._move_6 = bs.Timer(1800,bs.WeakCall(self._Left),repeat=False)
        self._move_7 = bs.Timer(1860,bs.WeakCall(self._Right),repeat=False)
        self._move_8 = bs.Timer(1920,bs.WeakCall(self._Left),repeat=False)
        self._move_9 = bs.Timer(1980,bs.WeakCall(self._Right),repeat=False)
        self._move_10 = bs.Timer(2040,bs.WeakCall(self._Left),repeat=False)
        self._move_11 = bs.Timer(2100,bs.WeakCall(self._Right),repeat=False)
        self._move_12 = bs.Timer(2160,bs.WeakCall(self._Left),repeat=False)
        self._move_13 = bs.Timer(2220,bs.WeakCall(self._Right),repeat=False)
        self._move_14 = bs.Timer(2280,bs.WeakCall(self._Left),repeat=False)
        self._move_15 = bs.Timer(2340,bs.WeakCall(self._Right),repeat=False)
        self._move_16 = bs.Timer(2400,bs.WeakCall(self._Left),repeat=False)
        self._move_17 = bs.Timer(2460,bs.WeakCall(self._Right),repeat=False)
        self._move_18 = bs.Timer(2520,bs.WeakCall(self._Left),repeat=False)
        self._move_19 = bs.Timer(2580,bs.WeakCall(self._Right),repeat=False)
        self._move_20 = bs.Timer(2640,bs.WeakCall(self._Left),repeat=False)
        self._move_21 = bs.Timer(2700,bs.WeakCall(self._Right),repeat=False)
        self._move_22 = bs.Timer(2760,bs.WeakCall(self._Left),repeat=False)
        self._move_23 = bs.Timer(2820,bs.WeakCall(self._Right),repeat=False)
        self._move_24 = bs.Timer(2880,bs.WeakCall(self._Left),repeat=False)
        self._move_25 = bs.Timer(2940,bs.WeakCall(self._stop),repeat=False)

    def _bug(self):
        self.node.run = 15
               
    def _offBug(self):
        self.node.run = 0

    def dropBomb(self):
        """
        Tell the spaz to drop one of his bombs, and returns
        the resulting bomb object.
        If the spaz has no bombs or is otherwise unable to
        drop a bomb, returns None.
        """

        if (self.landMineCount <= 0 and self.bombCount <= 0) or self.frozen:
            return
        p = self.node.positionForward
        v = self.node.velocity

        if self.landMineCount > 0:
            droppingBomb = False
            self.setLandMineCount(self.landMineCount-1)
            bombType = 'landMine'
        elif self.powerupBombCount > 0:
            droppingBomb = False
            self.setPowerupBombCount(self.powerupBombCount-1)
            bombType = 'powerupBomb'
        elif self.dirigidaCount > 0:
            droppingBomb = False
            self.setDirigidaCount(self.dirigidaCount-1)
            bombType = 'dirigida'
        else:
            droppingBomb = True
            bombType = self.bombType

        bomb = bs.Bomb(position=(p[0], p[1] - 0.0, p[2]),
                       velocity=(v[0], v[1], v[2]),
                       bombType=bombType,
                       blastRadius=self.blastRadius,
                       sourcePlayer=self.sourcePlayer,
                       owner=self.node).autoRetain()

        if droppingBomb:
            self.bombCount -= 1
            bomb.node.addDeathAction(bs.WeakCall(self.handleMessage,
                                                 _BombDiedMessage()))
        self._pickUp(bomb.node)

        for c in self._droppedBombCallbacks: c(self, bomb)
        
        return bomb

    def _pickUp(self, node):
        if self.node.exists() and node.exists():
            self.node.holdBody = 0 # needs to be set before holdNode
            self.node.holdNode = node
        
    def setLandMineCount(self, count):
        """
        Set the number of land-mines this spaz is carrying.
        """
        self.landMineCount = count
        if self.node.exists():
            if self.landMineCount != 0:
                self.node.counterText = 'x'+str(self.landMineCount)
                self.node.counterTexture = bs.Powerup.getFactory().texLandMines
            else:
                self.node.counterText = ''
                
    def setPowerupBombCount(self, count):
        self.powerupBombCount = count
        if self.node.exists():
            if self.powerupBombCount != 0:
                self.node.counterText = 'x'+str(self.powerupBombCount)
                self.node.counterTexture = bs.Powerup.getFactory().texPowerupBomb
            else:
                self.node.counterText = ''
                
    def setDirigidaCount(self, count):
        self.dirigidaCount = count
        if self.node.exists():
            if self.dirigidaCount != 0:
                self.node.counterText = 'x'+str(self.dirigidaCount)
                self.node.counterTexture = bs.Powerup.getFactory().texDirigida
            else:
                self.node.counterText = ''
                

    def curseExplode(self, sourcePlayer=None):
        """
        Explode the poor spaz as happens when
        a curse timer runs out.
        """

        # convert None to an empty player-ref
        if sourcePlayer is None: sourcePlayer = bs.Player(None)
        
        if self._cursed and self.node.exists():
            self.shatter(extreme=True)
            self.handleMessage(bs.DieMessage())
            activity = self._activity()
            if activity:
                bs.Blast(position=self.node.position,
                         velocity=self.node.velocity,
                         blastRadius=3.0, blastType='normal',
                         sourcePlayer=(sourcePlayer if sourcePlayer.exists()
                                       else self.sourcePlayer)).autoRetain()
            self._cursed = False

    def shatter(self, extreme=False):
        """
        Break the poor spaz into little bits.
        """
        if self.shattered: return
        self.shattered = True
        if self.frozen:
            # momentary flash of light
            light = bs.newNode('light',
                               attrs={'position':self.node.position,
                                      'radius':0.5,
                                      'heightAttenuated':False,
                                      'color': (0.8, 0.8, 1.0)})
            
            bs.animate(light, 'intensity', {0:3.0, 40:0.5, 80:0.07, 300:0})
            bs.gameTimer(300, light.delete)
            # emit ice chunks..
            bs.emitBGDynamics(position=self.node.position,
                              velocity=self.node.velocity,
                              count=int(random.random()*10.0+10.0),
                              scale=0.6, spread=0.2, chunkType='ice');
            bs.emitBGDynamics(position=self.node.position,
                              velocity=self.node.velocity,
                              count=int(random.random()*10.0+10.0),
                              scale=0.3, spread=0.2, chunkType='ice');

            bs.playSound(self.getFactory().shatterSound, 1.0,
                         position=self.node.position)
        else:
            bs.playSound(self.getFactory().splatterSound, 1.0,
                         position=self.node.position)
        self.handleMessage(bs.DieMessage())
        self.node.shattered = 2 if extreme else 1

    def _hitSelf(self, intensity):

        # clean exit if we're dead..
        try: pos = self.node.position
        except Exception: return

        self.handleMessage(bs.HitMessage(flatDamage=50.0*intensity,
                                         pos=pos,
                                         forceDirection=self.node.velocity,
                                         hitType='impact'))
        self.node.handleMessage("knockout", max(0.0, 50.0*intensity))
        if intensity > 5: sounds = self.getFactory().impactSoundsHarder
        elif intensity > 3: sounds = self.getFactory().impactSoundsHard
        else: sounds = self.getFactory().impactSoundsMedium
        s = sounds[random.randrange(len(sounds))]
        bs.playSound(s, position=pos, volume=5.0)
        
    def _getBombTypeTex(self):
        bombFactory = bs.Powerup.getFactory()
        if self.bombType == 'sticky': return bombFactory.texStickyBombs
        elif self.bombType == 'upSticky': return bombFactory.texStickyBombs
        elif self.bombType == 'ice': return bombFactory.texIceBombs
        elif self.bombType == 'impact': return bombFactory.texImpactBombs
        elif self.bombType == 'espectralBomb': return bombFactory.texUS
        elif self.bombType == 'magicBomb': return bombFactory.texDeathOrb
        elif self.bombType == 'iceImpact': return bombFactory.texIceImpact
        elif self.bombType == 'endBomb': return bombFactory.texSonicBomb
        elif self.bombType == 'tntImpact': return bombFactory.texTntBombs
        elif self.bombType == 'longWay': return bombFactory.texLongWayBombs
        elif self.bombType == 'saltarina': return bombFactory.texBombJumping
        elif self.bombType == 'electric': return bombFactory.texElectricBomb
        elif self.bombType == 'bugBomb': return bombFactory.texBB
        elif self.bombType == 'eggBomb': return bombFactory.texEgg
        elif self.bombType == 'dirigida': return bombFactory.texDirigida
        elif self.bombType == 'shockBomb': return bombFactory.texShock
        else: raise Exception()
        
    def _flashBillboard(self, tex):
        self.node.billboardTexture = tex
        self.node.billboardCrossOut = False
        bs.animate(self.node, "billboardOpacity",
                   {0:0.0, 100:1.0, 400:1.0, 500:0.0})

    def setBombCount(self, count):
        'Sets the number of bombs this Spaz has.'
        # we cant just set bombCount cuz some bombs may be laid currently
        # so we have to do a relative diff based on max
        diff = count - self._maxBombCount
        self._maxBombCount += diff
        self.bombCount += diff

    def _glovesWearOffFlash(self):
        if self.node.exists():
            self.node.boxingGlovesFlashing = 1
            self.node.billboardTexture = bs.Powerup.getFactory().texPunch
            self.node.billboardOpacity = 1.0
            self.node.billboardCrossOut = True

    def _glovesWearOff(self):
        if self._demoMode: # preserve old behavior
            self._punchPowerScale = gBasePunchPowerScale
            self._punchCooldown = gBasePunchCooldown
        else:
            factory = self.getFactory()
            self._punchPowerScale = factory.punchPowerScale
            self._punchCooldown = factory.punchCooldown
        self._hasBoxingGloves = False
        if self.node.exists():
            bs.playSound(bs.Powerup.getFactory().powerdownSound,
                         position=self.node.position)
            self.node.boxingGloves = 0
            self.node.billboardOpacity = 0.0

    def _multiBombWearOffFlash(self):
        if self.node.exists():
            self.node.billboardTexture = bs.Powerup.getFactory().texBomb
            self.node.billboardOpacity = 1.0
            self.node.billboardCrossOut = True

    def _multiBombWearOff(self):
        self.setBombCount(self.defaultBombCount)
        if self.node.exists():
            bs.playSound(bs.Powerup.getFactory().powerdownSound,
                         position=self.node.position)
            self.node.billboardOpacity = 0.0

    def _bombWearOffFlash(self):
        if self.node.exists():
            self.node.billboardTexture = self._getBombTypeTex()
            self.node.billboardOpacity = 1.0
            self.node.billboardCrossOut = True

    def _bombWearOff(self):
        self.bombType = self.bombTypeDefault
        if self.node.exists():
            bs.playSound(bs.Powerup.getFactory().powerdownSound,
                         position=self.node.position)
            self.node.billboardOpacity = 0.0
            
            ### MODS ###
    def _speedWearOffFlash(self):
        if self.node.exists():
            self.node.billboardTexture = bs.Powerup.getFactory().texSpeed
            self.node.billboardOpacity = 1.0
            self.node.billboardCrossOut = True

    def _speedWearOff(self):
        self.node.hockey = False
        if self.node.exists():
            bs.playSound(bs.Powerup.getFactory().powerdownSound,position=self.node.position)
            self.node.billboardOpacity = 0.0
            
    def _godWearOffFlash(self):
        if self.node.exists():
            self.node.billboardTexture = bs.Powerup.getFactory().texGod
            self.node.billboardOpacity = 1.0
            self.node.billboardCrossOut = True

    def _godWearOff(self):
        self.node.invincible = False
        if self.node.exists():
            bs.playSound(bs.Powerup.getFactory().powerdownSound,position=self.node.position)
            self.node.billboardOpacity = 0.0


class PlayerSpazDeathMessage(object):
    """
    category: Message Classes

    A bs.PlayerSpaz has died.

    Attributes:

       spaz
          The bs.PlayerSpaz that died.

       killed
          If True, the spaz was killed;
          If False, they left the game or the round ended.

       killerPlayer
          The bs.Player that did the killing, or None.

       how
          The particular type of death.
    """
    def __init__(self, spaz, wasKilled, killerPlayer, how):
        """
        Instantiate a message with the given values.
        """
        self.spaz = spaz
        self.killed = wasKilled
        self.killerPlayer = killerPlayer
        self.how = how

class PlayerSpazHurtMessage(object):
    """
    category: Message Classes

    A bs.PlayerSpaz was hurt.

    Attributes:

       spaz
          The bs.PlayerSpaz that was hurt
    """
    def __init__(self, spaz):
        """
        Instantiate with the given bs.Spaz value.
        """
        self.spaz = spaz


class PlayerSpaz(Spaz):
    """
    category: Game Flow Classes
    
    A bs.Spaz subclass meant to be controlled by a bs.Player.

    When a PlayerSpaz dies, it delivers a bs.PlayerSpazDeathMessage
    to the current bs.Activity. (unless the death was the result of the
    player leaving the game, in which case no message is sent)

    When a PlayerSpaz is hurt, it delivers a bs.PlayerSpazHurtMessage
    to the current bs.Activity.
    """


    def __init__(self, color=(1, 1, 1), highlight=(0.5, 0.5, 0.5),
                 character="Spaz", player=None, powerupsExpire=True):
        """
        Create a spaz for the provided bs.Player.
        Note: this does not wire up any controls;
        you must call connectControlsToPlayer() to do so.
        """
        # convert None to an empty player-ref
        if player is None: player = bs.Player(None)
        
        Spaz.__init__(self, color=color, highlight=highlight,
                      character=character, sourcePlayer=player,
                      startInvincible=True, powerupsExpire=powerupsExpire)
        self.lastPlayerAttackedBy = None # FIXME - should use empty player ref
        self.lastAttackedTime = 0
        self.lastAttackedType = None
        self.heldCount = 0
        self.lastPlayerHeldBy = None # FIXME - should use empty player ref here
        self._player = player

        # grab the node for this player and wire it to follow our spaz
        # (so players' controllers know where to draw their guides, etc)
        if player.exists():
            playerNode = bs.getActivity()._getPlayerNode(player)
            self.node.connectAttr('torsoPosition', playerNode, 'position')

    def __superHandleMessage(self, msg):
        super(PlayerSpaz, self).handleMessage(msg)
        
    def getPlayer(self):
        """
        Return the bs.Player associated with this spaz.
        Note that while a valid player object will always be
        returned, there is no guarantee that the player is still
        in the game.  Call bs.Player.exists() on the return value
        before doing anything with it.
        """
        return self._player

    def connectControlsToPlayer(self, enableJump=True, enablePunch=True,
                                enablePickUp=True, enableBomb=True,
                                enableRun=True, enableFly=True):
        """
        Wire this spaz up to the provided bs.Player.
        Full control of the character is given by default
        but can be selectively limited by passing False
        to specific arguments.
        """
        player = self.getPlayer()
        
        # reset any currently connected player and/or the player we're wiring up
        if self._connectedToPlayer is not None:
            if player != self._connectedToPlayer: player.resetInput()
            self.disconnectControlsFromPlayer()
        else: player.resetInput()

        player.assignInputCall('upDown', self.onMoveUpDown)
        player.assignInputCall('leftRight', self.onMoveLeftRight)
        player.assignInputCall('holdPositionPress', self._onHoldPositionPress)
        player.assignInputCall('holdPositionRelease',
                               self._onHoldPositionRelease)

        if enableJump:
            player.assignInputCall('jumpPress', self.onJumpPress)
            player.assignInputCall('jumpRelease', self.onJumpRelease)
        if enablePickUp:
            player.assignInputCall('pickUpPress', self.onPickUpPress)
            player.assignInputCall('pickUpRelease', self.onPickUpRelease)
        if enablePunch:
            player.assignInputCall('punchPress', self.onPunchPress)
            player.assignInputCall('punchRelease', self.onPunchRelease)
        if enableBomb:
            player.assignInputCall('bombPress', self.onBombPress)
            player.assignInputCall('bombRelease', self.onBombRelease)
        if enableRun:
            player.assignInputCall('run', self.onRun)
        if enableFly:
            player.assignInputCall('flyPress', self.onFlyPress)
            player.assignInputCall('flyRelease', self.onFlyRelease)

        self._connectedToPlayer = player

        
    def disconnectControlsFromPlayer(self):
        """
        Completely sever any previously connected
        bs.Player from control of this spaz.
        """
        if self._connectedToPlayer is not None:
            self._connectedToPlayer.resetInput()
            self._connectedToPlayer = None
            # send releases for anything in case its held..
            self.onMoveUpDown(0)
            self.onMoveLeftRight(0)
            self._onHoldPositionRelease()
            self.onJumpRelease()
            self.onPickUpRelease()
            self.onPunchRelease()
            self.onBombRelease()
            self.onRun(0.0)
            self.onFlyRelease()
        else:
            print ('WARNING: disconnectControlsFromPlayer() called for'
                   ' non-connected player')

    def handleMessage(self, msg):
        self._handleMessageSanityCheck()
        # keep track of if we're being held and by who most recently
        if isinstance(msg, bs.PickedUpMessage):
            self.__superHandleMessage(msg) # augment standard behavior
            self.heldCount += 1
            pickedUpBy = msg.node.sourcePlayer
            if pickedUpBy is not None and pickedUpBy.exists():
                self.lastPlayerHeldBy = pickedUpBy
        elif isinstance(msg, bs.DroppedMessage):
            self.__superHandleMessage(msg) # augment standard behavior
            self.heldCount -= 1
            if self.heldCount < 0:
                print "ERROR: spaz heldCount < 0"
            # let's count someone dropping us as an attack..
            try: pickedUpBy = msg.node.sourcePlayer
            except Exception: pickedUpBy = None
            if pickedUpBy is not None and pickedUpBy.exists():
                self.lastPlayerAttackedBy = pickedUpBy
                self.lastAttackedTime = bs.getGameTime()
                self.lastAttackedType = ('pickedUp', 'default')
        elif isinstance(msg, bs.DieMessage):

            # report player deaths to the game
            if not self._dead:

                # immediate-mode or left-game deaths don't count as 'kills'
                killed = (msg.immediate==False and msg.how!='leftGame')

                activity = self._activity()

                if not killed:
                    killerPlayer = None
                else:
                    # if this player was being held at the time of death,
                    # the holder is the killer
                    if (self.heldCount > 0
                            and self.lastPlayerHeldBy is not None
                            and self.lastPlayerHeldBy.exists()):
                        killerPlayer = self.lastPlayerHeldBy
                    else:
                        # otherwise, if they were attacked by someone in the
                        # last few seconds, that person's the killer..
                        # otherwise it was a suicide.
                        # FIXME - currently disabling suicides in Co-Op since
                        # all bot kills would register as suicides; need to
                        # change this from lastPlayerAttackedBy to something
                        # like lastActorAttackedBy to fix that.
                        if (self.lastPlayerAttackedBy is not None
                                and self.lastPlayerAttackedBy.exists()
                                and bs.getGameTime() - self.lastAttackedTime \
                                < 4000):
                            killerPlayer = self.lastPlayerAttackedBy
                        else:
                            # ok, call it a suicide unless we're in co-op
                            if (activity is not None
                                    and not isinstance(activity.getSession(),
                                                       bs.CoopSession)):
                                killerPlayer = self.getPlayer()
                            else:
                                killerPlayer = None
                            
                if killerPlayer is not None and not killerPlayer.exists():
                    killerPlayer = None

                # only report if both the player and the activity still exist
                if (killed and activity is not None
                    and self.getPlayer().exists()):
                    activity.handleMessage(
                        PlayerSpazDeathMessage(self, killed,
                                               killerPlayer, msg.how))
                    
            self.__superHandleMessage(msg) # augment standard behavior

        # keep track of the player who last hit us for point rewarding
        elif isinstance(msg, bs.HitMessage):
            if msg.sourcePlayer is not None and msg.sourcePlayer.exists():
                self.lastPlayerAttackedBy = msg.sourcePlayer
                self.lastAttackedTime = bs.getGameTime()
                self.lastAttackedType = (msg.hitType, msg.hitSubType)
            self.__superHandleMessage(msg) # augment standard behavior
            activity = self._activity()
            if activity is not None:
                activity.handleMessage(PlayerSpazHurtMessage(self))
        else:
            Spaz.handleMessage(self, msg)


class RespawnIcon(object):
    """
    category: Game Flow Classes

    An icon with a countdown that appears alongside the screen;
    used to indicate that a bs.Player is waiting to respawn.
    """
    
    def __init__(self, player, respawnTime):
        """
        Instantiate with a given bs.Player and respawnTime (in milliseconds)
        """
        activity = bs.getActivity()
        onRight = False
        self._visible = True
        if isinstance(bs.getSession(), bs.TeamsSession):
            onRight = player.getTeam().getID()%2==1
            # store a list of icons in the team
            try:
                respawnIcons = (player.getTeam()
                                .gameData['_spazRespawnIconsRight'])
            except Exception:
                respawnIcons = (player.getTeam()
                                .gameData['_spazRespawnIconsRight']) = {}
            offsExtra = -20
        else:
            onRight = False
            # store a list of icons in the activity
            try: respawnIcons = activity._spazRespawnIconsRight
            except Exception:
                respawnIcons = activity._spazRespawnIconsRight = {}
            if isinstance(activity.getSession(), bs.FreeForAllSession):
                offsExtra = -150
            else: offsExtra = -20

        try:
            maskTex = player.getTeam().gameData['_spazRespawnIconsMaskTex']
        except Exception:
            maskTex = player.getTeam().gameData['_spazRespawnIconsMaskTex'] = \
                bs.getTexture('characterIconMask')

        # now find the first unused slot and use that
        index = 0
        while (index in respawnIcons and respawnIcons[index]() is not None
               and respawnIcons[index]()._visible):
            index += 1
        respawnIcons[index] = weakref.ref(self)

        offs = offsExtra + index*-53
        icon = player.getIcon()
        texture = icon['texture']
        hOffs = -10
        self._image = bs.NodeActor(
            bs.newNode('image',
                       attrs={'texture':texture,
                              'tintTexture':icon['tintTexture'],
                              'tintColor':icon['tintColor'],
                              'tint2Color':icon['tint2Color'],
                              'maskTexture':maskTex,
                              'position':(-40-hOffs if onRight
                                          else 40+hOffs, -180+offs),
                              'scale':(32, 32),
                              'opacity':1.0,
                              'absoluteScale':True,
                              'attach':'topRight' if onRight else 'topLeft'}))
        
        bs.animate(self._image.node, 'opacity', {0:0, 200:0.7})

        self._name = bs.NodeActor(
            bs.newNode('text',
                       attrs={'vAttach':'top',
                              'hAttach':'right' if onRight else 'left',
                              'text':bs.Lstr(value=player.getName()),
                              'maxWidth':100,
                              'hAlign':'center',
                              'vAlign':'center',
                              'shadow':1.0,
                              'flatness':1.0,
                              'color':bs.getSafeColor(icon['tintColor']),
                              'scale':0.5,
                              'position':(-40-hOffs if onRight
                                          else 40+hOffs, -205+49+offs)}))
        
        bs.animate(self._name.node, 'scale', {0:0, 100:0.5})

        self._text = bs.NodeActor(
            bs.newNode('text',
                       attrs={'position':(-60-hOffs if onRight
                                          else 60+hOffs, -192+offs),
                              'hAttach':'right' if onRight else 'left',
                              'hAlign':'right' if onRight else 'left',
                              'scale':0.9,
                              'shadow':0.5,
                              'flatness':0.5,
                              'vAttach':'top',
                              'color':bs.getSafeColor(icon['tintColor']),
                              'text':''}))
        
        bs.animate(self._text.node, 'scale', {0:0, 100:0.9})

        self._respawnTime = bs.getGameTime()+respawnTime
        self._update()
        self._timer = bs.Timer(1000, bs.WeakCall(self._update), repeat=True)

    def _update(self):
        remaining = int(round(self._respawnTime-bs.getGameTime())/1000.0)
        if remaining > 0:
            if self._text.node.exists():
                self._text.node.text = str(remaining)
        else: self._clear()
            
    def _clear(self):
        self._visible = False
        self._image = self._text = self._timer = self._name = None
        


class SpazBotPunchedMessage(object):
    """
    category: Message Classes

    A bs.SpazBot got punched.

    Attributes:

       badGuy
          The bs.SpazBot that got punched.

       damage
          How much damage was done to the bs.SpazBot.
    """
    
    def __init__(self, badGuy, damage):
        """
        Instantiate a message with the given values.
        """
        self.badGuy = badGuy
        self.damage = damage

class SpazBotDeathMessage(object):
    """
    category: Message Classes

    A bs.SpazBot has died.

    Attributes:

       badGuy
          The bs.SpazBot that was killed.

       killerPlayer
          The bs.Player that killed it (or None).

       how
          The particular type of death.
    """
    
    def __init__(self, badGuy, killerPlayer, how):
        """
        Instantiate with given values.
        """
        self.badGuy = badGuy
        self.killerPlayer = killerPlayer
        self.how = how

        
class SpazBot(Spaz):
    """
    category: Bot Classes

    A really dumb AI version of bs.Spaz.
    Add these to a bs.BotSet to use them.

    Note: currently the AI has no real ability to
    navigate obstacles and so should only be used
    on wide-open maps.

    When a SpazBot is killed, it delivers a bs.SpazBotDeathMessage
    to the current activity.

    When a SpazBot is punched, it delivers a bs.SpazBotPunchedMessage
    to the current activity.
    """

    character = 'Spaz'
    punchiness = 0.5
    throwiness = 0.7
    static = False
    bouncy = False
    run = False
    chargeDistMin = 0.0 # when we can start a new charge
    chargeDistMax = 2.0 # when we can start a new charge
    runDistMin = 0.0 # how close we can be to continue running
    chargeSpeedMin = 0.4
    chargeSpeedMax = 1.0
    throwDistMin = 5.0
    throwDistMax = 9.0
    throwRate = 1.0
    defaultBombType = 'normal'
    defaultBombCount = 3
    startCursed = False
    color=gDefaultBotColor
    highlight=gDefaultBotHighlight

    def __init__(self):
        """
        Instantiate a spaz-bot.
        """
        Spaz.__init__(self, color=self.color, highlight=self.highlight,
                      character=self.character, sourcePlayer=None,
                      startInvincible=False, canAcceptPowerups=False)

        # if you need to add custom behavior to a bot, set this to a callable
        # which takes one arg (the bot) and returns False if the bot's normal
        # update should be run and True if not
        self.updateCallback = None
        self._map = weakref.ref(bs.getActivity().getMap())

        self.lastPlayerAttackedBy = None # FIXME - should use empty player-refs
        self.lastAttackedTime = 0
        self.lastAttackedType = None
        self.targetPointDefault = None
        self.heldCount = 0
        self.lastPlayerHeldBy = None # FIXME - should use empty player-refs here
        self.targetFlag = None
        self._chargeSpeed = 0.5*(self.chargeSpeedMin+self.chargeSpeedMax)
        self._leadAmount = 0.5
        self._mode = 'wait'
        self._chargeClosingIn = False
        self._lastChargeDist = 0.0
        self._running = False
        self._lastJumpTime = 0

        # these cooldowns didnt exist when these bots were calibrated,
        # so take them out of the equation
        self._jumpCooldown = 0
        self._pickupCooldown = 0
        self._flyCooldown = 0
        self._bombCooldown = 0

        if self.startCursed: self.curse()
            
    def _getTargetPlayerPt(self):
        """ returns the default player pt we're targeting """
        bp = bs.Vector(*self.node.position)
        closestLen = None
        closestVel = None
        for pp, pv in self._playerPts:

            l = (pp-bp).length()
            # ignore player-points that are significantly below the bot
            # (keeps bots from following players off cliffs)
            if (closestLen is None or l < closestLen) and (pp[1] > bp[1] - 5.0):
                closestLen = l
                closestVel = pv
                closest = pp
        if closestLen is not None:
            return (bs.Vector(closest[0], closest[1], closest[2]),
                    bs.Vector(closestVel[0], closestVel[1], closestVel[2]))
        else:
            return None, None

    def _setPlayerPts(self, pts):
        """
        Provide the spaz-bot with the locations of players.
        """
        self._playerPts = pts

    def _updateAI(self):
        """
        Should be called periodically to update the spaz' AI
        """
        
        if self.updateCallback is not None:
            if self.updateCallback(self) == True:
                return # true means bot has been handled

        t = self.node.position
        ourPos = bs.Vector(t[0], 0, t[2])
        canAttack = True

        # if we're a flag-bearer, we're pretty simple-minded - just walk
        # towards the flag and try to pick it up
        if self.targetFlag is not None:

            if not self.targetFlag.node.exists():
                # our flag musta died :-C
                self.targetFlag = None
                return
            if self.node.holdNode.exists():
                try: holdingFlag = (self.node.holdNode.getNodeType() == 'flag')
                except Exception: holdingFlag = False
            else: holdingFlag = False
            # if we're holding the flag, just walk left
            if holdingFlag:
                # just walk left
                self.node.moveLeftRight = -1.0
                self.node.moveUpDown = 0.0
            # otherwise try to go pick it up
            else:
                targetPtRaw = bs.Vector(*self.targetFlag.node.position)
                targetVel = bs.Vector(0, 0, 0)
                diff = (targetPtRaw-ourPos)
                diff = bs.Vector(diff[0], 0, diff[2]) # dont care about y
                dist = diff.length()
                toTarget = diff.normal()

                # if we're holding some non-flag item, drop it
                if self.node.holdNode.exists():
                    self.node.pickUpPressed = True
                    self.node.pickUpPressed = False
                    return

                # if we're a runner, run only when not super-near the flag
                if self.run and dist > 3.0:
                    self._running = True
                    self.node.run = 1.0
                else:
                    self._running = False
                    self.node.run = 0.0

                self.node.moveLeftRight = toTarget.x()
                self.node.moveUpDown = -toTarget.z()
                if dist < 1.25:
                    self.node.pickUpPressed = True
                    self.node.pickUpPressed = False
            return
        # not a flag-bearer.. if we're holding anything but a bomb, drop it
        else:
            if self.node.holdNode.exists():
                try: holdingBomb = \
                   (self.node.holdNode.getNodeType() in ['bomb', 'prop'])
                except Exception: holdingBomb = False
                if not holdingBomb:
                    self.node.pickUpPressed = True
                    self.node.pickUpPressed = False
                    return
            
        targetPtRaw, targetVel = self._getTargetPlayerPt()

        if targetPtRaw is None:
            # use default target if we've got one
            if self.targetPointDefault is not None:
                targetPtRaw = self.targetPointDefault
                targetVel = bs.Vector(0, 0, 0)
                canAttack = False
            # with no target, we stop moving and drop whatever we're holding
            else:
                self.node.moveLeftRight = 0
                self.node.moveUpDown = 0
                if self.node.holdNode.exists():
                    self.node.pickUpPressed = True
                    self.node.pickUpPressed = False
                return

        # we dont want height to come into play
        targetPtRaw.data[1] = 0
        targetVel.data[1] = 0

        distRaw = (targetPtRaw-ourPos).length()
        # use a point out in front of them as real target
        # (more out in front the farther from us they are)
        targetPt = targetPtRaw + targetVel*distRaw*0.3*self._leadAmount

        diff = (targetPt-ourPos)
        dist = diff.length()
        toTarget = diff.normal()

        if self._mode == 'throw':
            # we can only throw if alive and well..
            if not self._dead and not self.node.knockout:

                timeTillThrow = self._throwReleaseTime-bs.getGameTime()

                if not self.node.holdNode.exists():
                    # if we havnt thrown yet, whip out the bomb
                    if not self._haveDroppedThrowBomb:
                        self.dropBomb()
                        self._haveDroppedThrowBomb = True
                    # otherwise our lack of held node means we successfully
                    # released our bomb.. lets retreat now
                    else:
                        self._mode = 'flee'

                # oh crap we're holding a bomb.. better throw it.
                elif timeTillThrow <= 0:
                    # jump and throw..
                    def _safePickup(node):
                        if node.exists():
                            self.node.pickUpPressed = True
                            self.node.pickUpPressed = False
                    if dist > 5.0:
                        self.node.jumpPressed = True
                        self.node.jumpPressed = False
                        # throws:
                        bs.gameTimer(100, bs.Call(_safePickup, self.node))
                    else:
                        # throws:
                        bs.gameTimer(1, bs.Call(_safePickup, self.node))

                if self.static:
                    if timeTillThrow < 300:
                        speed = 1.0
                    elif timeTillThrow < 700 and dist > 3.0:
                        speed = -1.0 # whiplash for long throws
                    else:
                        speed = 0.02
                else:
                    if timeTillThrow < 700:
                        # right before throw charge full speed towards target
                        speed = 1.0
                    else:
                        # earlier we can hold or move backward for a whiplash
                        speed = 0.0125
                self.node.moveLeftRight = toTarget.x() * speed
                self.node.moveUpDown = toTarget.z() * -1.0 * speed

        elif self._mode == 'charge':
            if random.random() < 0.3:
                self._chargeSpeed = random.uniform(self.chargeSpeedMin,
                                                   self.chargeSpeedMax)
                # if we're a runner we run during charges *except when near
                # an edge (otherwise we tend to fly off easily)
                if self.run and distRaw > self.runDistMin:
                    self._leadAmount = 0.3
                    self._running = True
                    self.node.run = 1.0
                else:
                    self._leadAmont = 0.01
                    self._running = False
                    self.node.run = 0.0

            self.node.moveLeftRight = toTarget.x() * self._chargeSpeed
            self.node.moveUpDown = toTarget.z() * -1.0*self._chargeSpeed

        elif self._mode == 'wait':
            # every now and then, aim towards our target..
            # other than that, just stand there
            if bs.getGameTime()%1234 < 100:
                self.node.moveLeftRight = toTarget.x() * (400.0/33000)
                self.node.moveUpDown = toTarget.z() * (-400.0/33000)
            else:
                self.node.moveLeftRight = 0
                self.node.moveUpDown = 0

        elif self._mode == 'flee':
            # even if we're a runner, only run till we get away from our
            # target (if we keep running we tend to run off edges)
            if self.run and dist < 3.0:
                self._running = True
                self.node.run = 1.0
            else:
                self._running = False
                self.node.run = 0.0
            self.node.moveLeftRight = toTarget.x() * -1.0
            self.node.moveUpDown = toTarget.z()

        # we might wanna switch states unless we're doing a throw
        # (in which case thats our sole concern)
        if self._mode != 'throw':

            # if we're currently charging, keep track of how far we are
            # from our target.. when this value increases it means our charge
            # is over (ran by them or something)
            if self._mode == 'charge':
                if (self._chargeClosingIn and dist < 3.0
                        and dist > self._lastChargeDist):
                    self._chargeClosingIn = False
                self._lastChargeDist = dist

            # if we have a clean shot, throw!
            if (dist >= self.throwDistMin and dist < self.throwDistMax
                and random.random() < self.throwiness and canAttack):
                self._mode = 'throw'
                self._leadAmount = ((0.4+random.random()*0.6) if distRaw > 4.0
                                    else (0.1+random.random()*0.4))
                self._haveDroppedThrowBomb = False
                self._throwReleaseTime = (bs.getGameTime()
                                          + (1.0/self.throwRate)
                                          *(800 + int(1300*random.random())))

            # if we're static, always charge (which for us means barely move)
            elif self.static:
                self._mode = 'wait'
                
            # if we're too close to charge (and arent in the middle of an
            # existing charge) run away
            elif dist < self.chargeDistMin and not self._chargeClosingIn:
                # ..unless we're near an edge, in which case we got no choice
                # but to charge..
                if self._map()._isPointNearEdge(ourPos, self._running):
                    if self._mode != 'charge':
                        self._mode = 'charge'
                        self._leadAmount = 0.2
                        self._chargeClosingIn = True
                        self._lastChargeDist = dist
                else:
                    self._mode = 'flee'

            # we're within charging distance, backed against an edge, or farther
            # than our max throw distance.. chaaarge!
            elif (dist < self.chargeDistMax
                  or dist > self.throwDistMax
                  or self._map()._isPointNearEdge(ourPos, self._running)):
                if self._mode != 'charge':
                    self._mode = 'charge'
                    self._leadAmount = 0.01
                    self._chargeClosingIn = True
                    self._lastChargeDist = dist

            # we're too close to throw but too far to charge - either run
            # away or just chill if we're near an edge
            elif dist < self.throwDistMin:
                # charge if either we're within charge range or
                # cant retreat to throw
                self._mode = 'flee'

            # do some awesome jumps if we're running
            if ((self._running
                 and dist > 1.2 and dist < 2.2
                 and bs.getGameTime()-self._lastJumpTime > 1000)
                or (self.bouncy
                    and bs.getGameTime()-self._lastJumpTime > 400
                    and random.random() < 0.5)):
                self._lastJumpTime = bs.getGameTime()
                self.node.jumpPressed = True
                self.node.jumpPressed = False
                
            # throw punches when real close
            if dist < (1.6 if self._running else 1.2) and canAttack:
                if random.random() < self.punchiness:
                    self.onPunchPress()
                    self.onPunchRelease()

    def __superHandleMessage(self, msg):
        super(SpazBot, self).handleMessage(msg)

    def onPunched(self, damage):
        """
        Method override; sends bs.SpazBotPunchedMessage to the current activity.
        """
        bs.getActivity().handleMessage(SpazBotPunchedMessage(self, damage))

    def onFinalize(self):
        Spaz.onFinalize(self)
        # we're being torn down; release
        # our callback(s) so there's no chance of them
        # keeping activities or other things alive..
        self.updateCallback = None

    def handleMessage(self, msg):
        self._handleMessageSanityCheck()

        # keep track of if we're being held and by who most recently
        if isinstance(msg, bs.PickedUpMessage):
            self.__superHandleMessage(msg) # augment standard behavior
            self.heldCount += 1
            pickedUpBy = msg.node.sourcePlayer
            if pickedUpBy is not None and pickedUpBy.exists():
                self.lastPlayerHeldBy = pickedUpBy

        elif isinstance(msg, bs.DroppedMessage):
            self.__superHandleMessage(msg) # augment standard behavior
            self.heldCount -= 1
            if self.heldCount < 0:
                print "ERROR: spaz heldCount < 0"
            # let's count someone dropping us as an attack..
            try:
                if msg.node.exists(): pickedUpBy = msg.node.sourcePlayer
                else: pickedUpBy = bs.Player(None) # empty player ref
            except Exception as e:
                print 'EXC on SpazBot DroppedMessage:', e
                pickedUpBy = bs.Player(None) # empty player ref

            if pickedUpBy.exists():
                self.lastPlayerAttackedBy = pickedUpBy
                self.lastAttackedTime = bs.getGameTime()
                self.lastAttackedType = ('pickedUp', 'default')
            
        elif isinstance(msg, bs.DieMessage):

            # report normal deaths for scoring purposes
            if not self._dead and not msg.immediate:

                # if this guy was being held at the time of death, the
                # holder is the killer
                if (self.heldCount > 0 and self.lastPlayerHeldBy is not None
                        and self.lastPlayerHeldBy.exists()):
                    killerPlayer = self.lastPlayerHeldBy
                else:
                    # otherwise if they were attacked by someone in the
                    # last few seconds that person's the killer..
                    # otherwise it was a suicide
                    if (self.lastPlayerAttackedBy is not None
                           and self.lastPlayerAttackedBy.exists()
                           and bs.getGameTime() - self.lastAttackedTime < 4000):
                        killerPlayer = self.lastPlayerAttackedBy
                    else:
                        killerPlayer = None
                activity = self._activity()

                if killerPlayer is not None and not killerPlayer.exists():
                    killerPlayer = None
                if activity is not None:
                    if killerPlayer is not None: bs.statAdd('Bot Kills')
                    activity.handleMessage(
                        SpazBotDeathMessage(self, killerPlayer, msg.how))
            self.__superHandleMessage(msg) # augment standard behavior

        # keep track of the player who last hit us for point rewarding
        elif isinstance(msg, bs.HitMessage):
            if msg.sourcePlayer is not None and msg.sourcePlayer.exists():
                self.lastPlayerAttackedBy = msg.sourcePlayer
                self.lastAttackedTime = bs.getGameTime()
                self.lastAttackedType = (msg.hitType, msg.hitSubType)
            self.__superHandleMessage(msg)
        else:
            Spaz.handleMessage(self, msg)

            
class BomberBot(SpazBot):
    """
    category: Bot Classes
    
    A bot that throws regular bombs
    and occasionally punches.
    """
    character='Spaz'
    punchiness=0.3

    
class BomberBotLame(BomberBot):
    """
    category: Bot Classes
    
    A less aggressive yellow version of bs.BomberBot.
    """
    color=gLameBotColor
    highlight=gLameBotHighlight
    punchiness = 0.2
    throwRate = 0.7
    throwiness = 0.1
    chargeSpeedMin = 0.6
    chargeSpeedMax = 0.6

    
class BomberBotStaticLame(BomberBotLame):
    """
    category: Bot Classes
    
    A less aggressive yellow version of bs.BomberBot
    who generally stays in one place.
    """
    static = True
    throwDistMin = 0.0

    
class BomberBotStatic(BomberBot):
    """
    category: Bot Classes
    
    A version of bs.BomberBot
    who generally stays in one place.
    """
    static = True
    throwDistMin = 0.0


class BomberBotPro(BomberBot):
    """
    category: Bot Classes
    
    A more aggressive red version of bs.BomberBot.
    """
    pointsMult = 2
    color=gProBotColor
    highlight = gProBotHighlight
    defaultBombCount = 3
    defaultBoxingGloves = True
    punchiness = 0.7
    throwRate = 1.3
    run = True
    runDistMin = 6.0

    
class BomberBotProShielded(BomberBotPro):
    """
    category: Bot Classes
    
    A more aggressive red version of bs.BomberBot
    who starts with shields.
    """
    pointsMult = 3
    defaultShieldForBot = True

    
class BomberBotProStatic(BomberBotPro):
    """
    category: Bot Classes
    
    A more aggressive red version of bs.BomberBot
    who generally stays in one place.
    """
    static = True
    throwDistMin = 0.0

class BomberBotProStaticShielded(BomberBotProShielded):
    """
    category: Bot Classes
    
    A more aggressive red version of bs.BomberBot
    who starts with shields and
    who generally stays in one place.
    """
    static = True
    throwDistMin = 0.0

    
class ToughGuyBot(SpazBot):
    """
    category: Bot Classes
    
    A manly bot who walks and punches things.
    """
    character = 'Kronk'
    punchiness = 0.9
    chargeDistMax = 9999.0
    chargeSpeedMin = 1.0
    chargeSpeedMax = 1.0
    throwDistMin = 9999
    throwDistMax = 9999

    
class ToughGuyBotLame(ToughGuyBot):
    """
    category: Bot Classes
    
    A less aggressive yellow version of bs.ToughGuyBot.
    """
    color=gLameBotColor
    highlight=gLameBotHighlight
    punchiness = 0.3
    chargeSpeedMin = 0.6
    chargeSpeedMax = 0.6

    
class ToughGuyBotPro(ToughGuyBot):
    """
    category: Bot Classes
    
    A more aggressive red version of bs.ToughGuyBot.
    """
    color=gProBotColor
    highlight=gProBotHighlight
    run = True
    runDistMin = 4.0
    defaultBoxingGloves = True
    punchiness = 0.95
    pointsMult = 2

    
class ToughGuyBotProShielded(ToughGuyBotPro):
    """
    category: Bot Classes
    
    A more aggressive version of bs.ToughGuyBot
    who starts with shields.
    """
    defaultShieldForBot = True
    pointsMult = 3

    
class NinjaBot(SpazBot):
    """
    category: Bot Classes
    
    A speedy attacking melee bot.
    """

    character = 'Snake Shadow'
    punchiness = 1.0
    run = True
    chargeDistMin = 10.0
    chargeDistMax = 9999.0
    chargeSpeedMin = 1.0
    chargeSpeedMax = 1.0
    throwDistMin = 9999
    throwDistMax = 9999
    pointsMult = 2

    
class BunnyBot(SpazBot):
    """
    category: Bot Classes
    
    A speedy attacking melee bot.
    """

    color=(1, 1, 1)
    highlight=(1.0, 0.5, 0.5)
    character = 'Easter Bunny'
    punchiness = 1.0
    run = True
    bouncy = True
    defaultBoxingGloves = True
    chargeDistMin = 10.0
    chargeDistMax = 9999.0
    chargeSpeedMin = 1.0
    chargeSpeedMax = 1.0
    throwDistMin = 9999
    throwDistMax = 9999
    pointsMult = 2

    
class NinjaBotPro(NinjaBot):
    """
    category: Bot Classes
    
    A more aggressive red bs.NinjaBot.
    """
    color=gProBotColor
    highlight=gProBotHighlight
    defaultShieldForBot = True
    defaultBoxingGloves = True
    pointsMult = 3

    
class NinjaBotProShielded(NinjaBotPro):
    """
    category: Bot Classes
    
    A more aggressive red bs.NinjaBot
    who starts with shields.
    """
    defaultShieldForBot = True
    pointsMult = 4

    
class ChickBot(SpazBot):
    """
    category: Bot Classes
    
    A slow moving bot with impact bombs.
    """
    character = 'Zoe'
    punchiness = 0.75
    throwiness = 0.7
    chargeDistMax = 1.0
    chargeSpeedMin = 0.3
    chargeSpeedMax = 0.5
    throwDistMin = 3.5
    throwDistMax = 5.5
    defaultBombType = 'impact'
    pointsMult = 2

    
class ChickBotStatic(ChickBot):
    """
    category: Bot Classes
    
    A bs.ChickBot who generally stays in one place.
    """
    static = True
    throwDistMin = 0.0

    
class ChickBotPro(ChickBot):
    """
    category: Bot Classes
    
    A more aggressive red version of bs.ChickBot.
    """
    color=gProBotColor
    highlight=gProBotHighlight
    defaultBombCount = 3
    defaultBoxingGloves = True
    chargeSpeedMin = 1.0
    chargeSpeedMax = 1.0
    punchiness = 0.9
    throwRate = 1.3
    run = True
    runDistMin = 6.0
    pointsMult = 3

    
class ChickBotProShielded(ChickBotPro):
    """
    category: Bot Classes
    
    A more aggressive red version of bs.ChickBot
    who starts with shields.
    """
    defaultShieldForBot = True
    pointsMult = 4

    
class MelBot(SpazBot):
    """
    category: Bot Classes
    
    A crazy bot who runs and throws sticky bombs.
    """
    character = 'Mel'
    punchiness = 0.9
    throwiness = 1.0
    run = True
    chargeDistMin = 4.0
    chargeDistMax = 10.0
    chargeSpeedMin = 1.0
    chargeSpeedMax = 1.0
    throwDistMin = 0.0
    throwDistMax = 4.0
    throwRate = 2.0
    defaultBombType = 'sticky'
    defaultBombCount = 3
    pointsMult = 3

    
class MelBotStatic(MelBot):
    """
    category: Bot Classes
    
    A crazy bot who throws sticky-bombs but generally stays in one place.
    """
    static = True

    
class PirateBot(SpazBot):
    """
    category: Bot Classes
    
    A bot who runs and explodes in 5 seconds.
    """
    character = 'Jack Morgan'
    run = True
    chargeDistMin = 0.0
    chargeDistMax = 9999
    chargeSpeedMin = 1.0
    chargeSpeedMax = 1.0
    throwDistMin = 9999
    throwDistMax = 9999
    startCursed = True
    pointsMult = 4

    
class PirateBotNoTimeLimit(PirateBot):
    """
    category: Bot Classes
    
    A bot who runs but does not explode on his own.
    """
    curseTime = -1
    
    def handleMessage(self,m):
        super(self.__class__, self).handleMessage(m)
        self._color = bs.Timer(1000,bs.WeakCall(self._color),repeat=False)

    def _color(self):
        bsUtils.animateArray(self.node,'color',3,{0: self.node.color, 250:(9,0,0),500:self.node.color,750:self.node.color},True)

    
class PirateBotShielded(PirateBot):
    """
    category: Bot Classes
    
    A bs.PirateBot who starts with shields.
    """
    defaultShieldForBot = True
    pointsMult = 5

    
# Modpack exclusive bots ###########################
################################################
    
class NeonBot(SpazBot):
    """
    category: Bot Classes
    
    A manly bot who walks and punches things.
    """
    character = random.choice(['Spaz','Kronk','B-9000','Bernard','Pascal','Pixel'])
    color=(random.random()*20,random.random()*20,random.random()*20)
    highlight=(random.random()*20,random.random()*20,random.random()*20)
    punchiness = 0.9
    chargeDistMax = 9999.0
    chargeSpeedMin = 1.0
    chargeSpeedMax = 1.0
    throwDistMin = 9999
    throwDistMax = 9999
    
class Neon2Bot(SpazBot):
    """
    category: Bot Classes
    
    A manly bot who walks and punches things.
    """
    character = random.choice(['Spaz','Kronk','B-9000','Bernard','Pascal','Pixel'])
    color=(random.random()*20,random.random()*20,random.random()*20)
    highlight=(random.random()*20,random.random()*20,random.random()*20)
    punchiness = 0.9
    chargeDistMax = 9999.0
    chargeSpeedMin = 1.0
    chargeSpeedMax = 1.0
    throwDistMin = 9999
    throwDistMax = 9999
    
class Neon3Bot(SpazBot):
    """
    category: Bot Classes
    
    A manly bot who walks and punches things.
    """
    character = random.choice(['Spaz','Kronk','B-9000','Bernard','Pascal','Pixel'])
    color=(random.random()*20,random.random()*20,random.random()*20)
    highlight=(random.random()*20,random.random()*20,random.random()*20)
    punchiness = 0.9
    chargeDistMax = 9999.0
    chargeSpeedMin = 1.0
    chargeSpeedMax = 1.0
    throwDistMin = 9999
    throwDistMax = 9999
    
class SuicideBot(PirateBot):
    """
    category: Bot Classes
    
    A bot who runs but does not explode on his own.
    """
    character = 'Suicida'

class SuicideBomberBot(BomberBotPro):
    """
    category: Bot Classes
    
    A bot who runs but does not explode on his own.
    """
    character = 'Suicida'
    bombType = 'tntImpact'
    defaultShieldLevel4 = True
    
class PutininBot(NinjaBot):
    """
    category: Bot Classes
    
    A bot who runs but does not explode on his own.
    """
    character = 'Pixel 2'

class BearBot(SpazBot):
    """
    category: Bot Classes
    
    A cuty bear bot can drop cube bombs.
    """

    color=(0.4,0.2,0.1)
    highlight=(0,1,0)
    character = 'Bernard'
    punchiness = 0
    throwiness = 0.7
    chargeDistMax = 1.0
    chargeSpeedMin = 0.3
    chargeSpeedMax = 0.5
    throwDistMin = 3.5
    throwDistMax = 5.5
    defaultBombType = 'powerupBomb'
    pointsMult = 2

class BearBotPro(BearBot):
    """
    category: Bot Classes
    
    A bear very crazy
    """

    color=(0.6,0.3,0.15)
    highlight=(0,1,0)
    character = 'Bernard'
    punchiness = 0.9
    throwiness = 1.2
    run = True
    pointsMult = 3
    defaultBoxingGloves = True
    defaultBombCount = 5
    
class FrostyBot(SpazBot):
    """
    category: Bot Classes
    
    A bot that throws regular bombs
    and occasionally punches.
    """
    character='Frosty'
    punchiness=0.3
    defaultBombType = 'ice'

    
class FrostyBotLame(FrostyBot):
    """
    category: Bot Classes
    
    A less aggressive yellow version of bs.BomberBot.
    """
    color=(0,0,0)
    highlight=(1,1,1)
    punchiness = 0.2
    throwRate = 0.7
    throwiness = 0.1
    chargeSpeedMin = 0.6
    chargeSpeedMax = 0.6

    
class FrostyBotStaticLame(FrostyBotLame):
    """
    category: Bot Classes
    
    A less aggressive yellow version of bs.BomberBot
    who generally stays in one place.
    """
    static = True
    throwDistMin = 0.0

    
class FrostyBotStatic(FrostyBot):
    """
    category: Bot Classes
    
    A version of bs.BomberBot
    who generally stays in one place.
    """
    static = True
    throwDistMin = 0.0


class FrostyBotPro(FrostyBot):
    """
    category: Bot Classes
    
    A more aggressive red version of bs.BomberBot.
    """
    pointsMult = 2
    color=(0,0,0)
    highlight = (0,0,0)
    defaultBombCount = 3
    defaultBoxingGloves = True
    punchiness = 0.7
    throwRate = 1.3
    run = True
    runDistMin = 6.0

    
class FrostyBotProShielded(FrostyBotPro):
    """
    category: Bot Classes
    
    A more aggressive red version of bs.BomberBot
    who starts with shields.
    """
    pointsMult = 3
    defaultShieldForBot = True

    
class FrostyBotProStatic(FrostyBotPro):
    """
    category: Bot Classes
    
    A more aggressive red version of bs.BomberBot
    who generally stays in one place.
    """
    static = True
    throwDistMin = 0.0

class FrostyBotProStaticShielded(FrostyBotProShielded):
    """
    category: Bot Classes
    
    A more aggressive red version of bs.BomberBot
    who starts with shields and
    who generally stays in one place.
    """
    static = True
    throwDistMin = 0.0
    
class PascalBot(ToughGuyBot):
    color=(0,0,0)
    highlight=(0,0,0)
    character = 'Pascal'
    run = True
    punchiness = 0.8
    throwiness = 0.1
    chargeSpeedMin = 0.5
    chargeSpeedMax = 0.8
    
    def handleMessage(self,m):
        if isinstance(m, _PunchHitMessage):
            node = bs.getCollisionInfo("opposingNode")
            try:
                node.handleMessage(bs.FreezeMessage())
                bs.playSound(bs.getSound('freeze'))
            except Exception: print('Cant freeze')
            super(self.__class__, self).handleMessage(m)
        elif isinstance(m, bs.FreezeMessage):pass
        else: super(self.__class__, self).handleMessage(m)
        
class MostroBot(SpazBot):
    """
    category: Bot Classes
    
    A bot that throws regular bombs
    and occasionally punches.
    """
    character='Mostro'
    punchiness=0.3
    defaultBombType = 'mostro'
    

class MostroBotPro(MostroBot):
    """
    category: Bot Classes
    
    A more aggressive red version of bs.BomberBot.
    """
    pointsMult = 2
    color=(0,0,0)
    highlight = (0,0,0)
    defaultBombCount = 3
    defaultBoxingGloves = True
    punchiness = 0.7
    throwRate = 1.3
    run = True
    runDistMin = 6.0
        
class OsoMatonBot(ToughGuyBot):
    color=(0,0,0)
    highlight=(0,1,1)
    #name = 'Oso maton'
    character = 'Bernard'
    run = True
    punchiness = 0.8
    throwiness = 0.1
    chargeSpeedMin = 0.5
    chargeSpeedMax = 0.8
    defaultShieldLevel4 = False
    _punchPowerScale = 2
    hitPoints = 1500
    
    def handleMessage(self,m):
        super(self.__class__, self).handleMessage(m)
        self._nameColor = bs.Timer(10,bs.WeakCall(self._NC),repeat=False)

    def _NC(self):
    	self.node.name = 'Oso maton'
        self.node.nameColor = (0.75,0.75,0.75)
        #bsUtils.animateArray(self.node,'color',3,{0: self.node.color, 250:(9,0,0),500:self.node.color,750:self.node.color},True)
        
class BOSSBot(ToughGuyBotLame):
    color=(0,0,0)
    highlight=(0,1,1)
    character = 'Bernard'
    run = False
    punchiness = 0.8
    throwiness = 0.1
    chargeSpeedMin = 0.5
    chargeSpeedMax = 0.8
    defaultShieldLevel1 = True
    _punchPowerScale = 2
    hitPoints = 1500
    
    def handleMessage(self,m):
    	if isinstance(m, bs.OutOfBoundsMessage): self.teleport()
        else: super(self.__class__, self).handleMessage(m)
        #super(self.__class__, self).handleMessage(m)
        self._name = bs.Timer(500,bs.WeakCall(self._CT),repeat=False)
        self._color = bs.Timer(5000,bs.WeakCall(self._CK),repeat=False)
        self._muerte = bs.Timer(90000,bs.WeakCall(self._muerte),repeat=False)
        self._invoc = bs.Timer(12000,bs.WeakCall(self._invocate),repeat=False)
    	

    def _CT(self):
    	self.node.name = 'BOSS'
        self.node.nameColor = (1,1,1)
        self.hitPoints = -1
        #self.hitPoints =self.hitPointsMax = 10000
    	#self.node.handleMessage('celebrate',3000)
        #bsUtils.animateArray(self.node,'color',3,{0: self.node.color, 1000:(0,9,9),3000:self.node.color})
        
    def _CK(self):
    	#self.node.name = 'BOSS'
        #self.node.nameColor = (1,1,1)
        #self.hitPoints =self.hitPointsMax = 10000
    	self.node.handleMessage('celebrate',3000)
        bsUtils.animateArray(self.node,'color',3,{0: self.node.color, 1000:(0,9,9),3000:self.node.color})
        bs.getActivity()._botSet = bs.BotSet()
        bs.getActivity()._botSet.spawnBot(NoFrostyBot,pos=(self.node.position[0]+2,self.node.position[1],self.node.position[2]+2),spawnTime=1000)
        bs.getActivity()._botSet.spawnBot(NoFrostyBot,pos=(self.node.position[0]-2,self.node.position[1],self.node.position[2]-2),spawnTime=1500)
        bs.getActivity()._botSet.spawnBot(NoFrostyBot,pos=(self.node.position[0]+2,self.node.position[1],self.node.position[2]-2),spawnTime=2000)
        bs.getActivity()._botSet.spawnBot(NoFrostyBot,pos=(self.node.position[0]-2,self.node.position[1],self.node.position[2]+2),spawnTime=2500)
        bs.getActivity()._botSet.spawnBot(BonesBot,pos=(self.node.position[0]+2,self.node.position[1],self.node.position[2]-2),spawnTime=3500)
        bs.getActivity()._botSet.spawnBot(SuicideBot,pos=(self.node.position[0]-2,self.node.position[1],self.node.position[2]),spawnTime=4500)
        bs.getActivity()._botSet.spawnBot(BearBotPro,pos=(self.node.position[0]+3,self.node.position[1],self.node.position[2]+3),spawnTime=5500)
        bs.getActivity()._botSet.spawnBot(FrostyBot,pos=(self.node.position[0],self.node.position[1],self.node.position[2]+3),spawnTime=6500)
        bs.getActivity()._botSet.spawnBot(NoFrostyBot,pos=(self.node.position[0]+2,self.node.position[1],self.node.position[2]+2),spawnTime=7500)
        
    def shatter(self,extreme=False): return
        
    def teleport(self):
        self.handleMessage(bs.StandMessage(position = (random.uniform(-2,2),2.5,random.uniform(-2,2))))
        bs.playSound(bs.getSound('shieldHit'))
        bs.Blast(position = self.node.position,blastRadius = 0.2)
        
    def _muerte(self):
        self.handleMessage(bs.DieMessage())
        
    def _invocate(self):
        bs.Powerup(position=(self.node.position[0]+2,self.node.position[1],self.node.position[2]+2),powerupType='curse').autoRetain()
        bs.Powerup(position=(self.node.position[0]-2,self.node.position[1],self.node.position[2]-2),powerupType='curse').autoRetain()
        bs.Powerup(position=(self.node.position[0]+2,self.node.position[1],self.node.position[2]-2),powerupType='curse').autoRetain()
        bs.Powerup(position=(self.node.position[0]-2,self.node.position[1],self.node.position[2]+2),powerupType='curse').autoRetain()
    
    
class DAVRBot(ToughGuyBot):
    color=(0,1.2,0)
    highlight=(0,0,0)
    #name = 'Oso maton'
    character = 'Panda'
    run = True
    punchiness = 0.8
    throwiness = 0.1
    chargeSpeedMin = 0.5
    chargeSpeedMax = 0.8
    defaultShieldLevel4 = False
    _punchPowerScale = 2
    hitPoints = 1500
    
    def handleMessage(self,m):
        super(self.__class__, self).handleMessage(m)
        self._nameColor = bs.Timer(10,bs.WeakCall(self._NC),repeat=False)

    def _NC(self):
    	self.node.name = 'D. A. V. R.'
        self.node.nameColor = (0,1,0)
        
class CelyBot(ToughGuyBot):
    color=(1,1,1)
    highlight=(0,1*3,0.5*3)
    #name = 'Oso maton'
    character = 'Panda'
    run = True
    punchiness = 0.8
    throwiness = 0.1
    chargeSpeedMin = 0.5
    chargeSpeedMax = 0.8
    defaultShieldLevel4 = False
    _punchPowerScale = 2
    hitPoints = 1500
    
    def handleMessage(self,m):
        super(self.__class__, self).handleMessage(m)
        self._nameColor = bs.Timer(10,bs.WeakCall(self._NC),repeat=False)

    def _NC(self):
    	self.node.name = 'AleXis'
        self.node.nameColor = (1,1,1)
        
        
class OsoCulionBot(ToughGuyBot):
    color=(1,1,1)
    highlight=(0,1,1)
    #name = 'Oso maton'
    character = 'Bernard'
    run = True
    punchiness = 0.8
    throwiness = 0.1
    chargeSpeedMin = 0.5
    chargeSpeedMax = 0.8
    defaultShieldLevel4 = False
    _punchPowerScale = 2
    hitPoints = 1500
    
    def handleMessage(self,m):
        super(self.__class__, self).handleMessage(m)
        self._nameColor = bs.Timer(10,bs.WeakCall(self._NC),repeat=False)

    def _NC(self):
    	self.node.name = 'Oso culion'
        self.node.nameColor = (1,1,1)  
        
class OsaMatonaBot(ToughGuyBot):
    color=(1,0.3,0.5)
    highlight=(0.5,0.25,1)
    #name = 'Oso maton'
    character = 'Bernard'
    run = True
    punchiness = 0.8
    throwiness = 0.1
    chargeSpeedMin = 0.5
    chargeSpeedMax = 0.8
    defaultShieldLevel4 = False
    _punchPowerScale = 2
    hitPoints = 1500
    
    def handleMessage(self,m):
        super(self.__class__, self).handleMessage(m)
        self._nameColor = bs.Timer(10,bs.WeakCall(self._NC),repeat=False)

    def _NC(self):
    	self.node.name = 'Osa matona'
        self.node.nameColor = (1,0.3,0.5)
    
    
class OsoEspectroBot(ToughGuyBot):
    color=(0,1*9,1*9)
    highlight=(0,1*9,1*9)
    #name = 'Oso maton'
    character = 'Bernard'
    run = True
    punchiness = 0.8
    throwiness = 0.1
    chargeSpeedMin = 0.5
    chargeSpeedMax = 0.8
    defaultShieldLevel4 = False
    _punchPowerScale = 2
    hitPoints = 1500
    
    def handleMessage(self,m):
        super(self.__class__, self).handleMessage(m)
        self._nameColor = bs.Timer(10,bs.WeakCall(self._NC),repeat=False)

    def _NC(self):
    	self.node.name = 'Oso Espectro'
        self.node.nameColor = (0,1.5,1.5)
        
        
class EggBot(BomberBot):
    """
    category: Bot Classes
    
    A more aggressive red version of bs.ChickBot.
    """
    color=(0.9,0.4,0.4)
    highlight=(0,1*2,0)
    character='Easter Bunny'
    defaultBombCount = 5
    defaultBombType = 'eggBomb'
    defaultBoxingGloves = True
    chargeSpeedMin = 1.0
    chargeSpeedMax = 1.0
    punchiness = 0.9
    throwRate = 1.3
    run = True
    runDistMin = 6.0
    pointsMult = 2
    
    
class WizardBot(SpazBot):
    """
    category: Bot Classes
    
    A bot that throws regular bombs
    and occasionally punches.
    """
    character='Grumbledorf'
    punchiness=0.3
    defaultBombType = 'magicBomb'
    
class WizardBotPro(WizardBot):
    """
    category: Bot Classes
    
    A more aggressive red version of bs.ChickBot.
    """
    color=random.choice([(1,0,0),(0,1,0),(0,0,1),(1,1,1),(0,0,0),(1,1,0),(1,0,1),(0,1,1) ])
    highlight=(1*2,0,0)
    defaultBombCount = 5
    defaultBoxingGloves = True
    chargeSpeedMin = 1.0
    chargeSpeedMax = 1.0
    punchiness = 0.9
    throwRate = 1.3
    run = True
    runDistMin = 6.0
    pointsMult = 2
    
class BonesBot(ToughGuyBot):
    """
    category: Bot Classes
    
    A very resistant bot that slowly moves towards the player and hits hard with his Boxing Gloves.
    """ 
    character = 'Bones'
    impactScale = 0.75
    defaultBoxingGloves = True
    
class NoFrostyBot(ToughGuyBot):
    """
    category: Bot Classes
    
    A speedy attacking melee bot.
    """

    color=(1,0.5,0)
    highlight=(1.0, 0,0)
    character = 'Frosty??'
    punchiness = 1.0
    run = True
    bouncy = True
    defaultBoxingGloves = True
    chargeDistMin = 10.0
    chargeDistMax = 9999.0
    chargeSpeedMin = 1.0
    chargeSpeedMax = 1.0
    throwDistMin = 9999
    throwDistMax = 9999
    pointsMult = 2
   

class KillerBot(ToughGuyBot):
    color=(10,0,0)
    highlight=(10,1,0)
    #name = 'Oso maton'
    character = 'Bernard'
    run = True
    punchiness = 10
    throwiness = 0.1
    chargeSpeedMin = 0.5
    chargeSpeedMax = 1.8
    defaultShieldLevel4 = False
    hitPoints = 100
    
    def handleMessage(self,m):
        super(self.__class__, self).handleMessage(m)
        self._nameColor = bs.Timer(10,bs.WeakCall(self._NC),repeat=False)

    def _NC(self):
    	self.node.name = 'The Killer'
        self.node.nameColor = (1,0,0)
        self._punchPowerScale = 5
        
        
class BotSet(object):
    """
    category: Bot Classes
    
    A container/controller for one or more bs.SpazBots.
    """
    def __init__(self):
        """
        Create a bot-set.
        """
        # we spread our bots out over a few lists so we can update
        # them in a staggered fashion
        self._botListCount = 5
        self._botAddList = 0
        self._botUpdateList = 0
        self._botLists = [[] for i in range(self._botListCount)]
        self._spawnSound = bs.getSound('spawn')
        self._spawningCount = 0
        self.startMoving()

    def __del__(self):
        self.clear()

    def spawnBot(self, botType, pos, spawnTime=3000, onSpawnCall=None):
        """
        Spawn a bot from this set.
        """
        bsUtils.Spawner(pt=pos, spawnTime=spawnTime,
                        sendSpawnMessage=False,
                        spawnCallback=bs.Call(self._spawnBot, botType,
                                              pos, onSpawnCall))
        self._spawningCount += 1

    def _spawnBot(self, botType, pos, onSpawnCall):
        spaz = botType()
        bs.playSound(self._spawnSound, position=pos)
        spaz.node.handleMessage("flash")
        spaz.node.isAreaOfInterest = 0
        spaz.handleMessage(bs.StandMessage(pos, random.uniform(0, 360)))
        self.addBot(spaz)
        self._spawningCount -= 1
        if onSpawnCall is not None: onSpawnCall(spaz)
        
    def haveLivingBots(self):
        """
        Returns whether any bots in the set are alive or spawning.
        """
        haveLiving = any((any((not a._dead for a in l))
                          for l in self._botLists))
        haveSpawning = True if self._spawningCount > 0 else False
        return (haveLiving or haveSpawning)


    def getLivingBots(self):
        """
        Returns the living bots in the set.
        """
        bots = []
        for l in self._botLists:
            for b in l:
                if not b._dead: bots.append(b)
        return bots

    def _update(self):

        # update one of our bot lists each time through..
        # first off, remove dead bots from the list
        # (we check exists() here instead of dead.. we want to keep them
        # around even if they're just a corpse)
        try:
            botList = self._botLists[self._botUpdateList] = \
                [b for b in self._botLists[self._botUpdateList] if b.exists()]
        except Exception:
            bs.printException("error updating bot list: "
                              +str(self._botLists[self._botUpdateList]))
        self._botUpdateList = (self._botUpdateList+1)%self._botListCount

        # update our list of player points for the bots to use
        playerPts = []
        for player in bs.getActivity().players:
            try:
                if player.isAlive():
                    playerPts.append((bs.Vector(*player.actor.node.position),
                                     bs.Vector(*player.actor.node.velocity)))
            except Exception:
                bs.printException('error on bot-set _update')

        for b in botList:
            b._setPlayerPts(playerPts)
            b._updateAI()

    def clear(self):
        """
        Immediately clear out any bots in the set.
        """
        # dont do this if the activity is shutting down or dead
        activity = bs.getActivity(exceptionOnNone=False)
        if activity is None or activity.isFinalized(): return
        
        for i in range(len(self._botLists)):
            for b in self._botLists[i]:
                b.handleMessage(bs.DieMessage(immediate=True))
            self._botLists[i] = []
        
    def celebrate(self, duration):
        """
        Tell all living bots in the set to celebrate momentarily
        while continuing onward with their evil bot activities.
        """
        for l in self._botLists:
            for b in l:
                if b.node.exists():
                    b.node.handleMessage('celebrate', duration)

    def startMoving(self):
        """
        Starts processing bot AI updates and let them start doing their thing.
        """
        self._botUpdateTimer = bs.Timer(50, bs.WeakCall(self._update),
                                        repeat=True)
                    
    def stopMoving(self):
        """
        Tell all bots to stop moving and stops
        updating their AI.
        Useful when players have won and you want the
        enemy bots to just stand and look bewildered.
        """
        self._botUpdateTimer = None
        for l in self._botLists:
            for b in l:
                if b.node.exists():
                    b.node.moveLeftRight = 0
                    b.node.moveUpDown = 0
        
    def finalCelebrate(self):
        """
        Tell all bots in the set to stop what they were doing
        and just jump around and celebrate.  Use this when
        the bots have won a game.
        """
        self._botUpdateTimer = None
        # at this point stop doing anything but jumping and celebrating
        for l in self._botLists:
            for b in l:
                if b.node.exists():
                    b.node.moveLeftRight = 0
                    b.node.moveUpDown = 0
                    bs.gameTimer(random.randrange(0, 500),
                                 bs.Call(b.node.handleMessage,
                                         'celebrate', 10000))
                    jumpDuration = random.randrange(400, 500)
                    j = random.randrange(0, 200)
                    for i in range(10):
                        b.node.jumpPressed = True
                        b.node.jumpPressed = False
                        j += jumpDuration
                    bs.gameTimer(random.randrange(0, 1000),
                                 bs.Call(b.node.handleMessage, 'attackSound'))
                    bs.gameTimer(random.randrange(1000, 2000),
                                 bs.Call(b.node.handleMessage, 'attackSound'))
                    bs.gameTimer(random.randrange(2000, 3000),
                                 bs.Call(b.node.handleMessage, 'attackSound'))

    def addBot(self, bot):
        """
        Add a bs.SpazBot instance to the set.
        """
        self._botLists[self._botAddList].append(bot)
        self._botAddList = (self._botAddList+1)%self._botListCount

# define our built-in characters...

###############  SPAZ   ##################
t = Appearance("Spaz")

t.colorTexture = "neoSpazColor"
t.colorMaskTexture = "neoSpazColorMask"

t.iconTexture = "neoSpazIcon"
t.iconMaskTexture = "neoSpazIconColorMask"

t.headModel = "neoSpazHead"
t.torsoModel = "neoSpazTorso"
t.pelvisModel = "neoSpazPelvis"
t.upperArmModel = "neoSpazUpperArm"
t.foreArmModel = "neoSpazForeArm"
t.handModel = "neoSpazHand"
t.upperLegModel = "neoSpazUpperLeg"
t.lowerLegModel = "neoSpazLowerLeg"
t.toesModel = "neoSpazToes"

t.jumpSounds=["spazJump01",
              "spazJump02",
              "spazJump03",
              "spazJump04"]
t.attackSounds=["spazAttack01",
                "spazAttack02",
                "spazAttack03",
                "spazAttack04"]
t.impactSounds=["spazImpact01",
                "spazImpact02",
                "spazImpact03",
                "spazImpact04"]
t.deathSounds=["spazDeath01"]
t.pickupSounds=["spazPickup01"]
t.fallSounds=["spazFall01"]

t.style = 'spaz'


###############  Zoe   ##################
t = Appearance("Zoe")

t.colorTexture = "zoeColor"
t.colorMaskTexture = "zoeColorMask"

t.defaultColor = (0.6, 0.6, 0.6)
t.defaultHighlight = (0, 1, 0)

t.iconTexture = "zoeIcon"
t.iconMaskTexture = "zoeIconColorMask"

t.headModel = "zoeHead"
t.torsoModel = "zoeTorso"
t.pelvisModel = "zoePelvis"
t.upperArmModel = "zoeUpperArm"
t.foreArmModel = "zoeForeArm"
t.handModel = "zoeHand"
t.upperLegModel = "zoeUpperLeg"
t.lowerLegModel = "zoeLowerLeg"
t.toesModel = "zoeToes"

t.jumpSounds=["zoeJump01",
              "zoeJump02",
              "zoeJump03"]
t.attackSounds=["zoeAttack01",
                "zoeAttack02",
                "zoeAttack03",
                "zoeAttack04"]
t.impactSounds=["zoeImpact01",
                "zoeImpact02",
                "zoeImpact03",
                "zoeImpact04"]
t.deathSounds=["zoeDeath01"]
t.pickupSounds=["zoePickup01"]
t.fallSounds=["zoeFall01"]

t.style = 'female'


###############  Ninja   ##################
t = Appearance("Snake Shadow")

t.colorTexture = "ninjaColor"
t.colorMaskTexture = "ninjaColorMask"

t.defaultColor = (1, 1, 1)
t.defaultHighlight = (0.55, 0.8, 0.55)

t.iconTexture = "ninjaIcon"
t.iconMaskTexture = "ninjaIconColorMask"

t.headModel = "ninjaHead"
t.torsoModel = "ninjaTorso"
t.pelvisModel = "ninjaPelvis"
t.upperArmModel = "ninjaUpperArm"
t.foreArmModel = "ninjaForeArm"
t.handModel = "ninjaHand"
t.upperLegModel = "ninjaUpperLeg"
t.lowerLegModel = "ninjaLowerLeg"
t.toesModel = "ninjaToes"

ninjaAttacks = ['ninjaAttack'+str(i+1)+'' for i in range(7)]
ninjaHits = ['ninjaHit'+str(i+1)+'' for i in range(8)]
ninjaJumps = ['ninjaAttack'+str(i+1)+'' for i in range(7)]

t.jumpSounds=ninjaJumps
t.attackSounds=ninjaAttacks
t.impactSounds=ninjaHits
t.deathSounds=["ninjaDeath1"]
t.pickupSounds=ninjaAttacks
t.fallSounds=["ninjaFall1"]

t.style = 'ninja'


###############  Kronk   ##################
t = Appearance("Kronk")

t.colorTexture = "kronk"
t.colorMaskTexture = "kronkColorMask"

t.defaultColor = (0.4, 0.5, 0.4)
t.defaultHighlight = (1, 0.5, 0.3)

t.iconTexture = "kronkIcon"
t.iconMaskTexture = "kronkIconColorMask"

t.headModel = "kronkHead"
t.torsoModel = "kronkTorso"
t.pelvisModel = "kronkPelvis"
t.upperArmModel = "kronkUpperArm"
t.foreArmModel = "kronkForeArm"
t.handModel = "kronkHand"
t.upperLegModel = "kronkUpperLeg"
t.lowerLegModel = "kronkLowerLeg"
t.toesModel = "kronkToes"

kronkSounds = ["kronk1",
              "kronk2",
              "kronk3",
              "kronk4",
              "kronk5",
              "kronk6",
              "kronk7",
              "kronk8",
              "kronk9",
              "kronk10"]
t.jumpSounds=kronkSounds
t.attackSounds=kronkSounds
t.impactSounds=kronkSounds
t.deathSounds=["kronkDeath"]
t.pickupSounds=kronkSounds
t.fallSounds=["kronkFall"]

t.style = 'kronk'


###############  MEL   ##################
t = Appearance("Mel")

t.colorTexture = "melColor"
t.colorMaskTexture = "melColorMask"

t.defaultColor = (1, 1, 1)
t.defaultHighlight = (0.1, 0.6, 0.1)

t.iconTexture = "melIcon"
t.iconMaskTexture = "melIconColorMask"

t.headModel =     "melHead"
t.torsoModel =    "melTorso"
t.pelvisModel = "kronkPelvis"
t.upperArmModel = "melUpperArm"
t.foreArmModel =  "melForeArm"
t.handModel =     "melHand"
t.upperLegModel = "melUpperLeg"
t.lowerLegModel = "melLowerLeg"
t.toesModel =     "melToes"

melSounds = ["mel01",
              "mel02",
              "mel03",
              "mel04",
              "mel05",
              "mel06",
              "mel07",
              "mel08",
              "mel09",
              "mel10"]

t.attackSounds = melSounds
t.jumpSounds = melSounds
t.impactSounds = melSounds
t.deathSounds=["melDeath01"]
t.pickupSounds = melSounds
t.fallSounds=["melFall01"]

t.style = 'mel'


###############  Jack Morgan   ##################

t = Appearance("Jack Morgan")

t.colorTexture = "jackColor"
t.colorMaskTexture = "jackColorMask"

t.defaultColor = (1, 0.2, 0.1)
t.defaultHighlight = (1, 1, 0)

t.iconTexture = "jackIcon"
t.iconMaskTexture = "jackIconColorMask"

t.headModel =     "jackHead"
t.torsoModel =    "jackTorso"
t.pelvisModel = "kronkPelvis"
t.upperArmModel = "jackUpperArm"
t.foreArmModel =  "jackForeArm"
t.handModel =     "jackHand"
t.upperLegModel = "jackUpperLeg"
t.lowerLegModel = "jackLowerLeg"
t.toesModel =     "jackToes"

hitSounds = ["jackHit01",
             "jackHit02",
             "jackHit03",
             "jackHit04",
             "jackHit05",
             "jackHit06",
             "jackHit07"]

sounds = ["jack01",
          "jack02",
          "jack03",
          "jack04",
          "jack05",
          "jack06"]

t.attackSounds = sounds
t.jumpSounds = sounds
t.impactSounds = hitSounds
t.deathSounds=["jackDeath01"]
t.pickupSounds = sounds
t.fallSounds=["jackFall01"]

t.style = 'pirate'


###############  SANTA   ##################

t = Appearance("Santa Claus")

t.colorTexture = "santaColor"
t.colorMaskTexture = "santaColorMask"

t.defaultColor = (1, 0, 0)
t.defaultHighlight = (1, 1, 1)

t.iconTexture = "santaIcon"
t.iconMaskTexture = "santaIconColorMask"

t.headModel =     "santaHead"
t.torsoModel =    "santaTorso"
t.pelvisModel = "kronkPelvis"
t.upperArmModel = "santaUpperArm"
t.foreArmModel =  "santaForeArm"
t.handModel =     "santaHand"
t.upperLegModel = "santaUpperLeg"
t.lowerLegModel = "santaLowerLeg"
t.toesModel =     "santaToes"

hitSounds = ['santaHit01', 'santaHit02', 'santaHit03', 'santaHit04']
sounds = ['santa01', 'santa02', 'santa03', 'santa04', 'santa05']

t.attackSounds = sounds
t.jumpSounds = sounds
t.impactSounds = hitSounds
t.deathSounds=["santaDeath"]
t.pickupSounds = sounds
t.fallSounds=["santaFall"]

t.style = 'santa'

###############  FROSTY   ##################

t = Appearance("Frosty")

t.colorTexture = "frostyColor"
t.colorMaskTexture = "frostyColorMask"

t.defaultColor = (0.5, 0.5, 1)
t.defaultHighlight = (1, 0.5, 0)

t.iconTexture = "frostyIcon"
t.iconMaskTexture = "frostyIconColorMask"

t.headModel =     "frostyHead"
t.torsoModel =    "frostyTorso"
t.pelvisModel = "frostyPelvis"
t.upperArmModel = "frostyUpperArm"
t.foreArmModel =  "frostyForeArm"
t.handModel =     "frostyHand"
t.upperLegModel = "frostyUpperLeg"
t.lowerLegModel = "frostyLowerLeg"
t.toesModel =     "frostyToes"

frostySounds = ['frosty01', 'frosty02', 'frosty03', 'frosty04', 'frosty05']
frostyHitSounds = ['frostyHit01', 'frostyHit02', 'frostyHit03']

t.attackSounds = frostySounds
t.jumpSounds = frostySounds
t.impactSounds = frostyHitSounds
t.deathSounds=["frostyDeath"]
t.pickupSounds = frostySounds
t.fallSounds=["frostyFall"]

t.style = 'frosty'

###############  BONES  ##################

t = Appearance("Bones")

t.colorTexture = "bonesColor"
t.colorMaskTexture = "bonesColorMask"

t.defaultColor = (0.6, 0.9, 1)
t.defaultHighlight = (0.6, 0.9, 1)

t.iconTexture = "bonesIcon"
t.iconMaskTexture = "bonesIconColorMask"

t.headModel =     "bonesHead"
t.torsoModel =    "bonesTorso"
t.pelvisModel =   "bonesPelvis"
t.upperArmModel = "bonesUpperArm"
t.foreArmModel =  "bonesForeArm"
t.handModel =     "bonesHand"
t.upperLegModel = "bonesUpperLeg"
t.lowerLegModel = "bonesLowerLeg"
t.toesModel =     "bonesToes"

bonesSounds =    ['bones1', 'bones2', 'bones3']
bonesHitSounds = ['bones1', 'bones2', 'bones3']

t.attackSounds = bonesSounds
t.jumpSounds = bonesSounds
t.impactSounds = bonesHitSounds
t.deathSounds=["bonesDeath"]
t.pickupSounds = bonesSounds
t.fallSounds=["bonesFall"]

t.style = 'bones'

# bear ###################################

t = Appearance("Bernard")

t.colorTexture = "bearColor"
t.colorMaskTexture = "bearColorMask"

t.defaultColor = (0.7, 0.5, 0.0)
#t.defaultHighlight = (0.6, 0.5, 0.8)

t.iconTexture = "bearIcon"
t.iconMaskTexture = "bearIconColorMask"

t.headModel =     "bearHead"
t.torsoModel =    "bearTorso"
t.pelvisModel =   "bearPelvis"
t.upperArmModel = "bearUpperArm"
t.foreArmModel =  "bearForeArm"
t.handModel =     "bearHand"
t.upperLegModel = "bearUpperLeg"
t.lowerLegModel = "bearLowerLeg"
t.toesModel =     "bearToes"

bearSounds =    ['bear1', 'bear2', 'bear3', 'bear4']
bearHitSounds = ['bearHit1', 'bearHit2']

t.attackSounds = bearSounds
t.jumpSounds = bearSounds
t.impactSounds = bearHitSounds
t.deathSounds=["bearDeath"]
t.pickupSounds = bearSounds
t.fallSounds=["bearFall"]

t.style = 'bear'

# Penguin ###################################

t = Appearance("Pascal")

t.colorTexture = "penguinColor"
t.colorMaskTexture = "penguinColorMask"

t.defaultColor = (0.3, 0.5, 0.8)
t.defaultHighlight = (1, 0, 0)

t.iconTexture = "penguinIcon"
t.iconMaskTexture = "penguinIconColorMask"

t.headModel =     "penguinHead"
t.torsoModel =    "penguinTorso"
t.pelvisModel =   "penguinPelvis"
t.upperArmModel = "penguinUpperArm"
t.foreArmModel =  "penguinForeArm"
t.handModel =     "penguinHand"
t.upperLegModel = "penguinUpperLeg"
t.lowerLegModel = "penguinLowerLeg"
t.toesModel =     "penguinToes"

penguinSounds =    ['penguin1', 'penguin2', 'penguin3', 'penguin4']
penguinHitSounds = ['penguinHit1', 'penguinHit2']

t.attackSounds = penguinSounds
t.jumpSounds = penguinSounds
t.impactSounds = penguinHitSounds
t.deathSounds=["penguinDeath"]
t.pickupSounds = penguinSounds
t.fallSounds=["penguinFall"]

t.style = 'penguin'


# Ali ###################################
t = Appearance("Taobao Mascot")
t.colorTexture = "aliColor"
t.colorMaskTexture = "aliColorMask"
t.defaultColor = (1, 0.5, 0)
t.defaultHighlight = (1, 1, 1)
t.iconTexture = "aliIcon"
t.iconMaskTexture = "aliIconColorMask"
t.headModel =     "aliHead"
t.torsoModel =    "aliTorso"
t.pelvisModel =   "aliPelvis"
t.upperArmModel = "aliUpperArm"
t.foreArmModel =  "aliForeArm"
t.handModel =     "aliHand"
t.upperLegModel = "aliUpperLeg"
t.lowerLegModel = "aliLowerLeg"
t.toesModel =     "aliToes"
aliSounds =    ['ali1', 'ali2', 'ali3', 'ali4']
aliHitSounds = ['aliHit1', 'aliHit2']
t.attackSounds = aliSounds
t.jumpSounds = aliSounds
t.impactSounds = aliHitSounds
t.deathSounds=["aliDeath"]
t.pickupSounds = aliSounds
t.fallSounds=["aliFall"]
t.style = 'ali'

# cyborg ###################################
t = Appearance("B-9000")
t.colorTexture = "cyborgColor"
t.colorMaskTexture = "cyborgColorMask"
t.defaultColor = (0.5, 0.5, 0.5)
t.defaultHighlight = (1, 0, 0)
t.iconTexture = "cyborgIcon"
t.iconMaskTexture = "cyborgIconColorMask"
t.headModel =     "cyborgHead"
t.torsoModel =    "cyborgTorso"
t.pelvisModel =   "cyborgPelvis"
t.upperArmModel = "cyborgUpperArm"
t.foreArmModel =  "cyborgForeArm"
t.handModel =     "cyborgHand"
t.upperLegModel = "cyborgUpperLeg"
t.lowerLegModel = "cyborgLowerLeg"
t.toesModel =     "cyborgToes"
cyborgSounds =    ['cyborg1', 'cyborg2', 'cyborg3', 'cyborg4']
cyborgHitSounds = ['cyborgHit1', 'cyborgHit2']
t.attackSounds = cyborgSounds
t.jumpSounds = cyborgSounds
t.impactSounds = cyborgHitSounds
t.deathSounds=["cyborgDeath"]
t.pickupSounds = cyborgSounds
t.fallSounds=["cyborgFall"]
t.style = 'cyborg'

# Agent ###################################
t = Appearance("Agent Johnson")
t.colorTexture = "agentColor"
t.colorMaskTexture = "agentColorMask"
t.defaultColor = (0.3, 0.3, 0.33)
t.defaultHighlight = (1, 0.5, 0.3)
t.iconTexture = "agentIcon"
t.iconMaskTexture = "agentIconColorMask"
t.headModel =     "agentHead"
t.torsoModel =    "agentTorso"
t.pelvisModel =   "agentPelvis"
t.upperArmModel = "agentUpperArm"
t.foreArmModel =  "agentForeArm"
t.handModel =     "agentHand"
t.upperLegModel = "agentUpperLeg"
t.lowerLegModel = "agentLowerLeg"
t.toesModel =     "agentToes"
agentSounds =    ['agent1', 'agent2', 'agent3', 'agent4']
agentHitSounds = ['agentHit1', 'agentHit2']
t.attackSounds = agentSounds
t.jumpSounds = agentSounds
t.impactSounds = agentHitSounds
t.deathSounds=["agentDeath"]
t.pickupSounds = agentSounds
t.fallSounds=["agentFall"]
t.style = 'agent'

# Jumpsuit ###################################
t = Appearance("Lee")
t.colorTexture = "jumpsuitColor"
t.colorMaskTexture = "jumpsuitColorMask"
t.defaultColor = (0.3, 0.5, 0.8)
t.defaultHighlight = (1, 0, 0)
t.iconTexture = "jumpsuitIcon"
t.iconMaskTexture = "jumpsuitIconColorMask"
t.headModel =     "jumpsuitHead"
t.torsoModel =    "jumpsuitTorso"
t.pelvisModel =   "jumpsuitPelvis"
t.upperArmModel = "jumpsuitUpperArm"
t.foreArmModel =  "jumpsuitForeArm"
t.handModel =     "jumpsuitHand"
t.upperLegModel = "jumpsuitUpperLeg"
t.lowerLegModel = "jumpsuitLowerLeg"
t.toesModel =     "jumpsuitToes"
jumpsuitSounds = ['jumpsuit1', 'jumpsuit2', 'jumpsuit3', 'jumpsuit4']
jumpsuitHitSounds = ['jumpsuitHit1', 'jumpsuitHit2']
t.attackSounds = jumpsuitSounds
t.jumpSounds = jumpsuitSounds
t.impactSounds = jumpsuitHitSounds
t.deathSounds=["jumpsuitDeath"]
t.pickupSounds = jumpsuitSounds
t.fallSounds=["jumpsuitFall"]
t.style = 'spaz'

# ActionHero ###################################
t = Appearance("Todd McBurton")
t.colorTexture = "actionHeroColor"
t.colorMaskTexture = "actionHeroColorMask"
t.defaultColor = (0.3, 0.5, 0.8)
t.defaultHighlight = (1, 0, 0)
t.iconTexture = "actionHeroIcon"
t.iconMaskTexture = "actionHeroIconColorMask"
t.headModel =     "actionHeroHead"
t.torsoModel =    "actionHeroTorso"
t.pelvisModel =   "actionHeroPelvis"
t.upperArmModel = "actionHeroUpperArm"
t.foreArmModel =  "actionHeroForeArm"
t.handModel =     "actionHeroHand"
t.upperLegModel = "actionHeroUpperLeg"
t.lowerLegModel = "actionHeroLowerLeg"
t.toesModel =     "actionHeroToes"
actionHeroSounds = ['actionHero1', 'actionHero2', 'actionHero3', 'actionHero4']
actionHeroHitSounds = ['actionHeroHit1', 'actionHeroHit2']
t.attackSounds = actionHeroSounds
t.jumpSounds = actionHeroSounds
t.impactSounds = actionHeroHitSounds
t.deathSounds=["actionHeroDeath"]
t.pickupSounds = actionHeroSounds
t.fallSounds=["actionHeroFall"]
t.style = 'spaz'

# Assassin ###################################
t = Appearance("Zola")
t.colorTexture = "assassinColor"
t.colorMaskTexture = "assassinColorMask"
t.defaultColor = (0.3, 0.5, 0.8)
t.defaultHighlight = (1, 0, 0)
t.iconTexture = "assassinIcon"
t.iconMaskTexture = "assassinIconColorMask"
t.headModel =     "assassinHead"
t.torsoModel =    "assassinTorso"
t.pelvisModel =   "assassinPelvis"
t.upperArmModel = "assassinUpperArm"
t.foreArmModel =  "assassinForeArm"
t.handModel =     "assassinHand"
t.upperLegModel = "assassinUpperLeg"
t.lowerLegModel = "assassinLowerLeg"
t.toesModel =     "assassinToes"
assassinSounds = ['assassin1', 'assassin2', 'assassin3', 'assassin4']
assassinHitSounds = ['assassinHit1', 'assassinHit2']
t.attackSounds = assassinSounds
t.jumpSounds = assassinSounds
t.impactSounds = assassinHitSounds
t.deathSounds=["assassinDeath"]
t.pickupSounds = assassinSounds
t.fallSounds=["assassinFall"]
t.style = 'spaz'

# Wizard ###################################
t = Appearance("Grumbledorf")
t.colorTexture = "wizardColor"
t.colorMaskTexture = "wizardColorMask"
t.defaultColor = (0.2, 0.4, 1.0)
t.defaultHighlight = (0.06, 0.15, 0.4)
t.iconTexture = "wizardIcon"
t.iconMaskTexture = "wizardIconColorMask"
t.headModel =     "wizardHead"
t.torsoModel =    "wizardTorso"
t.pelvisModel =   "wizardPelvis"
t.upperArmModel = "wizardUpperArm"
t.foreArmModel =  "wizardForeArm"
t.handModel =     "wizardHand"
t.upperLegModel = "wizardUpperLeg"
t.lowerLegModel = "wizardLowerLeg"
t.toesModel =     "wizardToes"
wizardSounds =    ['wizard1', 'wizard2', 'wizard3', 'wizard4']
wizardHitSounds = ['wizardHit1', 'wizardHit2']
t.attackSounds = wizardSounds
t.jumpSounds = wizardSounds
t.impactSounds = wizardHitSounds
t.deathSounds=["wizardDeath"]
t.pickupSounds = wizardSounds
t.fallSounds=["wizardFall"]
t.style = 'spaz'

# Cowboy ###################################
t = Appearance("Butch")
t.colorTexture = "cowboyColor"
t.colorMaskTexture = "cowboyColorMask"
t.defaultColor = (0.3, 0.5, 0.8)
t.defaultHighlight = (1, 0, 0)
t.iconTexture = "cowboyIcon"
t.iconMaskTexture = "cowboyIconColorMask"
t.headModel =     "cowboyHead"
t.torsoModel =    "cowboyTorso"
t.pelvisModel =   "cowboyPelvis"
t.upperArmModel = "cowboyUpperArm"
t.foreArmModel =  "cowboyForeArm"
t.handModel =     "cowboyHand"
t.upperLegModel = "cowboyUpperLeg"
t.lowerLegModel = "cowboyLowerLeg"
t.toesModel =     "cowboyToes"
cowboySounds =    ['cowboy1', 'cowboy2', 'cowboy3', 'cowboy4']
cowboyHitSounds = ['cowboyHit1', 'cowboyHit2']
t.attackSounds = cowboySounds
t.jumpSounds = cowboySounds
t.impactSounds = cowboyHitSounds
t.deathSounds=["cowboyDeath"]
t.pickupSounds = cowboySounds
t.fallSounds=["cowboyFall"]
t.style = 'spaz'

# Witch ###################################
t = Appearance("Witch")
t.colorTexture = "witchColor"
t.colorMaskTexture = "witchColorMask"
t.defaultColor = (0.3, 0.5, 0.8)
t.defaultHighlight = (1, 0, 0)
t.iconTexture = "witchIcon"
t.iconMaskTexture = "witchIconColorMask"
t.headModel =     "witchHead"
t.torsoModel =    "witchTorso"
t.pelvisModel =   "witchPelvis"
t.upperArmModel = "witchUpperArm"
t.foreArmModel =  "witchForeArm"
t.handModel =     "witchHand"
t.upperLegModel = "witchUpperLeg"
t.lowerLegModel = "witchLowerLeg"
t.toesModel =     "witchToes"
witchSounds =    ['witch1', 'witch2', 'witch3', 'witch4']
witchHitSounds = ['witchHit1', 'witchHit2']
t.attackSounds = witchSounds
t.jumpSounds = witchSounds
t.impactSounds = witchHitSounds
t.deathSounds=["witchDeath"]
t.pickupSounds = witchSounds
t.fallSounds=["witchFall"]
t.style = 'spaz'

# Warrior ###################################
t = Appearance("Warrior")
t.colorTexture = "warriorColor"
t.colorMaskTexture = "warriorColorMask"
t.defaultColor = (0.3, 0.5, 0.8)
t.defaultHighlight = (1, 0, 0)
t.iconTexture = "warriorIcon"
t.iconMaskTexture = "warriorIconColorMask"
t.headModel =     "warriorHead"
t.torsoModel =    "warriorTorso"
t.pelvisModel =   "warriorPelvis"
t.upperArmModel = "warriorUpperArm"
t.foreArmModel =  "warriorForeArm"
t.handModel =     "warriorHand"
t.upperLegModel = "warriorUpperLeg"
t.lowerLegModel = "warriorLowerLeg"
t.toesModel =     "warriorToes"
warriorSounds =    ['warrior1', 'warrior2', 'warrior3', 'warrior4']
warriorHitSounds = ['warriorHit1', 'warriorHit2']
t.attackSounds = warriorSounds
t.jumpSounds = warriorSounds
t.impactSounds = warriorHitSounds
t.deathSounds=["warriorDeath"]
t.pickupSounds = warriorSounds
t.fallSounds=["warriorFall"]
t.style = 'spaz'

# Superhero ###################################
t = Appearance("Middle-Man")
t.colorTexture = "superheroColor"
t.colorMaskTexture = "superheroColorMask"
t.defaultColor = (0.3, 0.5, 0.8)
t.defaultHighlight = (1, 0, 0)
t.iconTexture = "superheroIcon"
t.iconMaskTexture = "superheroIconColorMask"
t.headModel =     "superheroHead"
t.torsoModel =    "superheroTorso"
t.pelvisModel =   "superheroPelvis"
t.upperArmModel = "superheroUpperArm"
t.foreArmModel =  "superheroForeArm"
t.handModel =     "superheroHand"
t.upperLegModel = "superheroUpperLeg"
t.lowerLegModel = "superheroLowerLeg"
t.toesModel =     "superheroToes"
superheroSounds =    ['superhero1', 'superhero2', 'superhero3', 'superhero4']
superheroHitSounds = ['superheroHit1', 'superheroHit2']
t.attackSounds = superheroSounds
t.jumpSounds = superheroSounds
t.impactSounds = superheroHitSounds
t.deathSounds=["superheroDeath"]
t.pickupSounds = superheroSounds
t.fallSounds=["superheroFall"]
t.style = 'spaz'

# Alien ###################################
t = Appearance("Alien")
t.colorTexture = "alienColor"
t.colorMaskTexture = "alienColorMask"
t.defaultColor = (0.3, 0.5, 0.8)
t.defaultHighlight = (1, 0, 0)
t.iconTexture = "alienIcon"
t.iconMaskTexture = "alienIconColorMask"
t.headModel =     "alienHead"
t.torsoModel =    "alienTorso"
t.pelvisModel =   "alienPelvis"
t.upperArmModel = "alienUpperArm"
t.foreArmModel =  "alienForeArm"
t.handModel =     "alienHand"
t.upperLegModel = "alienUpperLeg"
t.lowerLegModel = "alienLowerLeg"
t.toesModel =     "alienToes"
alienSounds =    ['alien1', 'alien2', 'alien3', 'alien4']
alienHitSounds = ['alienHit1', 'alienHit2']
t.attackSounds = alienSounds
t.jumpSounds = alienSounds
t.impactSounds = alienHitSounds
t.deathSounds=["alienDeath"]
t.pickupSounds = alienSounds
t.fallSounds=["alienFall"]
t.style = 'spaz'

# OldLady ###################################
t = Appearance("OldLady")
t.colorTexture = "oldLadyColor"
t.colorMaskTexture = "oldLadyColorMask"
t.defaultColor = (0.3, 0.5, 0.8)
t.defaultHighlight = (1, 0, 0)
t.iconTexture = "oldLadyIcon"
t.iconMaskTexture = "oldLadyIconColorMask"
t.headModel =     "oldLadyHead"
t.torsoModel =    "oldLadyTorso"
t.pelvisModel =   "oldLadyPelvis"
t.upperArmModel = "oldLadyUpperArm"
t.foreArmModel =  "oldLadyForeArm"
t.handModel =     "oldLadyHand"
t.upperLegModel = "oldLadyUpperLeg"
t.lowerLegModel = "oldLadyLowerLeg"
t.toesModel =     "oldLadyToes"
oldLadySounds =    ['oldLady1', 'oldLady2', 'oldLady3', 'oldLady4']
oldLadyHitSounds = ['oldLadyHit1', 'oldLadyHit2']
t.attackSounds = oldLadySounds
t.jumpSounds = oldLadySounds
t.impactSounds = oldLadyHitSounds
t.deathSounds=["oldLadyDeath"]
t.pickupSounds = oldLadySounds
t.fallSounds=["oldLadyFall"]
t.style = 'spaz'

# Gladiator ###################################
t = Appearance("Gladiator")
t.colorTexture = "gladiatorColor"
t.colorMaskTexture = "gladiatorColorMask"
t.defaultColor = (0.3, 0.5, 0.8)
t.defaultHighlight = (1, 0, 0)
t.iconTexture = "gladiatorIcon"
t.iconMaskTexture = "gladiatorIconColorMask"
t.headModel =     "gladiatorHead"
t.torsoModel =    "gladiatorTorso"
t.pelvisModel =   "gladiatorPelvis"
t.upperArmModel = "gladiatorUpperArm"
t.foreArmModel =  "gladiatorForeArm"
t.handModel =     "gladiatorHand"
t.upperLegModel = "gladiatorUpperLeg"
t.lowerLegModel = "gladiatorLowerLeg"
t.toesModel =     "gladiatorToes"
gladiatorSounds =    ['gladiator1', 'gladiator2', 'gladiator3', 'gladiator4']
gladiatorHitSounds = ['gladiatorHit1', 'gladiatorHit2']
t.attackSounds = gladiatorSounds
t.jumpSounds = gladiatorSounds
t.impactSounds = gladiatorHitSounds
t.deathSounds=["gladiatorDeath"]
t.pickupSounds = gladiatorSounds
t.fallSounds=["gladiatorFall"]
t.style = 'spaz'

# Wrestler ###################################
t = Appearance("Wrestler")
t.colorTexture = "wrestlerColor"
t.colorMaskTexture = "wrestlerColorMask"
t.defaultColor = (0.3, 0.5, 0.8)
t.defaultHighlight = (1, 0, 0)
t.iconTexture = "wrestlerIcon"
t.iconMaskTexture = "wrestlerIconColorMask"
t.headModel =     "wrestlerHead"
t.torsoModel =    "wrestlerTorso"
t.pelvisModel =   "wrestlerPelvis"
t.upperArmModel = "wrestlerUpperArm"
t.foreArmModel =  "wrestlerForeArm"
t.handModel =     "wrestlerHand"
t.upperLegModel = "wrestlerUpperLeg"
t.lowerLegModel = "wrestlerLowerLeg"
t.toesModel =     "wrestlerToes"
wrestlerSounds =    ['wrestler1', 'wrestler2', 'wrestler3', 'wrestler4']
wrestlerHitSounds = ['wrestlerHit1', 'wrestlerHit2']
t.attackSounds = wrestlerSounds
t.jumpSounds = wrestlerSounds
t.impactSounds = wrestlerHitSounds
t.deathSounds=["wrestlerDeath"]
t.pickupSounds = wrestlerSounds
t.fallSounds=["wrestlerFall"]
t.style = 'spaz'

# OperaSinger ###################################
t = Appearance("Gretel")
t.colorTexture = "operaSingerColor"
t.colorMaskTexture = "operaSingerColorMask"
t.defaultColor = (0.3, 0.5, 0.8)
t.defaultHighlight = (1, 0, 0)
t.iconTexture = "operaSingerIcon"
t.iconMaskTexture = "operaSingerIconColorMask"
t.headModel =     "operaSingerHead"
t.torsoModel =    "operaSingerTorso"
t.pelvisModel =   "operaSingerPelvis"
t.upperArmModel = "operaSingerUpperArm"
t.foreArmModel =  "operaSingerForeArm"
t.handModel =     "operaSingerHand"
t.upperLegModel = "operaSingerUpperLeg"
t.lowerLegModel = "operaSingerLowerLeg"
t.toesModel =     "operaSingerToes"
operaSingerSounds =    ['operaSinger1', 'operaSinger2',
                        'operaSinger3', 'operaSinger4']
operaSingerHitSounds = ['operaSingerHit1', 'operaSingerHit2']
t.attackSounds = operaSingerSounds
t.jumpSounds = operaSingerSounds
t.impactSounds = operaSingerHitSounds
t.deathSounds=["operaSingerDeath"]
t.pickupSounds = operaSingerSounds
t.fallSounds=["operaSingerFall"]
t.style = 'spaz'

# Pixie ###################################
t = Appearance("Pixel")
t.colorTexture = "pixieColor"
t.colorMaskTexture = "pixieColorMask"
t.defaultColor = (0, 1, 0.7)
t.defaultHighlight = (0.65, 0.35, 0.75)
t.iconTexture = "pixieIcon"
t.iconMaskTexture = "pixieIconColorMask"
t.headModel =     "pixieHead"
t.torsoModel =    "pixieTorso"
t.pelvisModel =   "pixiePelvis"
t.upperArmModel = "pixieUpperArm"
t.foreArmModel =  "pixieForeArm"
t.handModel =     "pixieHand"
t.upperLegModel = "pixieUpperLeg"
t.lowerLegModel = "pixieLowerLeg"
t.toesModel =     "pixieToes"
pixieSounds =    ['pixie1', 'pixie2', 'pixie3', 'pixie4']
pixieHitSounds = ['pixieHit1', 'pixieHit2']
t.attackSounds = pixieSounds
t.jumpSounds = pixieSounds
t.impactSounds = pixieHitSounds
t.deathSounds=["pixieDeath"]
t.pickupSounds = pixieSounds
t.fallSounds=["pixieFall"]
t.style = 'pixie'

# Robot ###################################
t = Appearance("Robot")
t.colorTexture = "robotColor"
t.colorMaskTexture = "robotColorMask"
t.defaultColor = (0.3, 0.5, 0.8)
t.defaultHighlight = (1, 0, 0)
t.iconTexture = "robotIcon"
t.iconMaskTexture = "robotIconColorMask"
t.headModel =     "robotHead"
t.torsoModel =    "robotTorso"
t.pelvisModel =   "robotPelvis"
t.upperArmModel = "robotUpperArm"
t.foreArmModel =  "robotForeArm"
t.handModel =     "robotHand"
t.upperLegModel = "robotUpperLeg"
t.lowerLegModel = "robotLowerLeg"
t.toesModel =     "robotToes"
robotSounds =    ['robot1', 'robot2', 'robot3', 'robot4']
robotHitSounds = ['robotHit1', 'robotHit2']
t.attackSounds = robotSounds
t.jumpSounds = robotSounds
t.impactSounds = robotHitSounds
t.deathSounds=["robotDeath"]
t.pickupSounds = robotSounds
t.fallSounds=["robotFall"]
t.style = 'spaz'

# Bunny ###################################
t = Appearance("Easter Bunny")
t.colorTexture = "bunnyColor"
t.colorMaskTexture = "bunnyColorMask"
t.defaultColor = (1, 1, 1)
t.defaultHighlight = (1, 0.5, 0.5)
t.iconTexture = "bunnyIcon"
t.iconMaskTexture = "bunnyIconColorMask"
t.headModel =     "bunnyHead"
t.torsoModel =    "bunnyTorso"
t.pelvisModel =   "bunnyPelvis"
t.upperArmModel = "bunnyUpperArm"
t.foreArmModel =  "bunnyForeArm"
t.handModel =     "bunnyHand"
t.upperLegModel = "bunnyUpperLeg"
t.lowerLegModel = "bunnyLowerLeg"
t.toesModel =     "bunnyToes"
bunnySounds =    ['bunny1', 'bunny2', 'bunny3', 'bunny4']
bunnyHitSounds = ['bunnyHit1', 'bunnyHit2']
t.attackSounds = bunnySounds
t.jumpSounds = ['bunnyJump']
t.impactSounds = bunnyHitSounds
t.deathSounds=["bunnyDeath"]
t.pickupSounds = bunnySounds
t.fallSounds=["bunnyFall"]
t.style = 'bunny'

#######New Characters#################
######################################


# bear ###################################

t = Appearance("Oso Espectro")

t.colorTexture = "bearColor"
t.colorMaskTexture = "bearColorMask"

t.defaultColor = (0,1*3,1*3)
t.defaultHighlight = (0,1*3,1*3)

t.iconTexture = "bearIcon"
t.iconMaskTexture = "bearIconColorMask"

t.headModel =     "bearHead"
t.torsoModel =    "bearTorso"
t.pelvisModel =   "bearPelvis"
t.upperArmModel = "bearUpperArm"
t.foreArmModel =  "bearForeArm"
t.handModel =     "bearHand"
t.upperLegModel = "bearUpperLeg"
t.lowerLegModel = "bearLowerLeg"
t.toesModel =     "bearToes"

bearSounds =    ['bear1', 'bear2', 'bear3', 'bear4']
bearHitSounds = ['bearHit1', 'bearHit2']

t.attackSounds = bearSounds
t.jumpSounds = bearSounds
t.impactSounds = bearHitSounds
t.deathSounds=["bearDeath"]
t.pickupSounds = bearSounds
t.fallSounds=["bearFall"]

t.style = 'bear'

###############  Jack Morgan   ##################

t = Appearance("Suicida")

t.colorTexture = "tnt"
t.colorMaskTexture = "bunnyColorMask"

t.defaultColor = (1, 0.2, 0.1)
t.defaultHighlight = (1, 1, 0)

t.iconTexture = "tnt"
t.iconMaskTexture = "tnt"

t.headModel =     "powerup"
t.torsoModel =    "jackTorso"
t.pelvisModel = "kronkPelvis"
t.upperArmModel = "jackUpperArm"
t.foreArmModel =  "jackForeArm"
t.handModel =     "jackHand"
t.upperLegModel = "jackUpperLeg"
t.lowerLegModel = "jackLowerLeg"
t.toesModel =     "jackToes"

hitSounds = ["jackHit01",
             "jackHit02",
             "jackHit03",
             "jackHit04",
             "jackHit05",
             "jackHit06",
             "jackHit07"]

sounds = ["jack01",
          "jack02",
          "jack03",
          "jack04",
          "jack05",
          "jack06"]

t.attackSounds = sounds
t.jumpSounds = sounds
t.impactSounds = hitSounds
t.deathSounds=["jackDeath01"]
t.pickupSounds = sounds
t.fallSounds=["jackFall01"]

t.style = 'bones'

# Agent ###################################
t = Appearance("Mostro")
t.colorTexture = "warriorColor"
t.colorMaskTexture = "warriorColorMask"
t.defaultColor = (0.3, 0.3, 0.33)
t.defaultHighlight = (1, 0.5, 0.3)
t.iconTexture = "puckColor"
t.iconMaskTexture = "puckColor"
t.headModel =     "impactBomb"
t.torsoModel =    "impactBomb"
t.pelvisModel =   "impactBomb"
t.upperArmModel = "impactBomb"
t.foreArmModel =  "impactBomb"
t.handModel =     "impactBomb"
t.upperLegModel = "impactBomb"
t.lowerLegModel = "impactBomb"
t.toesModel =     "impactBomb"
agentSounds =    ['agent1', 'agent2', 'agent3', 'agent4']
agentHitSounds = ['agentHit1', 'agentHit2']
t.attackSounds = agentSounds
t.jumpSounds = agentSounds
t.impactSounds = agentHitSounds
t.deathSounds=["agentDeath"]
t.pickupSounds = agentSounds
t.fallSounds=["agentFall"]
t.style = 'cyborg'

###############  Kronk   ##################
t = Appearance("Fireman")

t.colorTexture = "aliColor"
t.colorMaskTexture = "kronkColorMask"

t.defaultColor = (0.4, 0.5, 0.4)
t.defaultHighlight = (1, 0.5, 0.3)

t.iconTexture = "kronkIcon"
t.iconMaskTexture = "aliColor"

t.headModel = "kronkHead"
t.torsoModel = "kronkTorso"
t.pelvisModel = "kronkPelvis"
t.upperArmModel = "kronkUpperArm"
t.foreArmModel = "kronkForeArm"
t.handModel = "kronkHand"
t.upperLegModel = "kronkUpperLeg"
t.lowerLegModel = "kronkLowerLeg"
t.toesModel = "kronkToes"

kronkSounds = ["kronk1",
              "kronk2",
              "kronk3",
              "kronk4",
              "kronk5",
              "kronk6",
              "kronk7",
              "kronk8",
              "kronk9",
              "kronk10"]
t.jumpSounds=kronkSounds
t.attackSounds=kronkSounds
t.impactSounds=kronkSounds
t.deathSounds=["kronkDeath"]
t.pickupSounds=kronkSounds
t.fallSounds=["kronkFall"]

t.style = 'kronk'

###############  FROSTY   ##################

t = Appearance("Frosty??")

t.colorTexture = "frostyColor"
t.colorMaskTexture = "kronkColorMask"

t.defaultColor = (0.5, 0.5, 1)
t.defaultHighlight = (1, 0.5, 0)

t.iconTexture = "frostyIcon"
t.iconMaskTexture = "frostyIconColorMask"

t.headModel =     "frostyHead"
t.torsoModel =    "kronkTorso"
t.pelvisModel = "kronkPelvis"
t.upperArmModel = "frostyUpperArm"
t.foreArmModel =  "frostyForeArm"
t.handModel =     "agentHand"
t.upperLegModel = "agentUpperLeg"
t.lowerLegModel = "agentLowerLeg"
t.toesModel =     "agentToes"

frostySounds = ['frosty01', 'frosty02', 'frosty03', 'frosty04', 'frosty05']
frostyHitSounds = ['frostyHit01', 'frostyHit02', 'frostyHit03']

t.attackSounds = frostySounds
t.jumpSounds = frostySounds
t.impactSounds = frostyHitSounds
t.deathSounds=["frostyDeath"]
t.pickupSounds = frostySounds
t.fallSounds=["frostyFall"]

t.style = 'frosty'


# Pixie ###################################
t = Appearance("Pixel 2")
t.colorTexture = "pixieColor"
t.colorMaskTexture = "pixieColorMask"
t.defaultColor = (0, 1, 0.7)
t.defaultHighlight = (0.65, 0.35, 0.75)
t.iconTexture = "pixieIcon"
t.iconMaskTexture = "pixieIconColorMask"
t.headModel =     "pixieHead"
t.torsoModel =    "pixieTorso"
t.pelvisModel =   "pixiePelvis"
t.upperArmModel = "pixieUpperArm"
t.foreArmModel =  "pixieForeArm"
t.handModel =     "pixieHand"
t.upperLegModel = "pixieUpperLeg"
t.lowerLegModel = "pixieLowerLeg"
t.toesModel =     "pixieToes"
pixieSounds =    ['pixie1', 'pixie2', 'pixie3', 'pixie4']
pixieHitSounds = ['pixieHit1', 'pixieHit2']
t.attackSounds = pixieSounds
t.jumpSounds = pixieSounds
t.impactSounds = pixieHitSounds
t.deathSounds=["pixieDeath"]
t.pickupSounds = pixieSounds
t.fallSounds=["pixieFall"]
t.style = 'female'

###############  Ninja   ##################
t = Appearance("Ninja Mariposa")

t.colorTexture = "ninjaColor"
t.colorMaskTexture = "ninjaColorMask"

t.defaultColor = (1, 1, 1)
t.defaultHighlight = (0.55, 0.8, 0.55)

t.iconTexture = "ninjaIcon"
t.iconMaskTexture = "ninjaIconColorMask"

t.headModel = "ninjaHead"
t.torsoModel = "ninjaTorso"
t.pelvisModel = "ninjaPelvis"
t.upperArmModel = "ninjaUpperArm"
t.foreArmModel = "ninjaForeArm"
t.handModel = "ninjaHand"
t.upperLegModel = "ninjaUpperLeg"
t.lowerLegModel = "ninjaLowerLeg"
t.toesModel = "ninjaToes"

ninjaAttacks = ['ninjaAttack'+str(i+1)+'' for i in range(7)]
ninjaHits = ['ninjaHit'+str(i+1)+'' for i in range(8)]
ninjaJumps = ['ninjaAttack'+str(i+1)+'' for i in range(7)]

t.jumpSounds=ninjaJumps
t.attackSounds=ninjaAttacks
t.impactSounds=ninjaHits
t.deathSounds=["ninjaDeath1"]
t.pickupSounds=ninjaAttacks
t.fallSounds=["ninjaFall1"]

t.style = 'pixie'

###############  Kronk   ##################
t = Appearance("Kronka")

t.colorTexture = "kronk"
t.colorMaskTexture = "kronkColorMask"

t.defaultColor = (0.4, 0.5, 0.4)
t.defaultHighlight = (1, 0.5, 0.3)

t.iconTexture = "kronkIcon"
t.iconMaskTexture = "kronkIconColorMask"

t.headModel = "kronkHead"
t.torsoModel = "kronkTorso"
t.pelvisModel = "kronkPelvis"
t.upperArmModel = "kronkUpperArm"
t.foreArmModel = "kronkForeArm"
t.handModel = "kronkHand"
t.upperLegModel = "kronkUpperLeg"
t.lowerLegModel = "kronkLowerLeg"
t.toesModel = "kronkToes"

kronkSounds = ["kronk1",
              "kronk2",
              "kronk3",
              "kronk4",
              "kronk5",
              "kronk6",
              "kronk7",
              "kronk8",
              "kronk9",
              "kronk10"]
t.jumpSounds=kronkSounds
t.attackSounds=kronkSounds
t.impactSounds=kronkSounds
t.deathSounds=["kronkDeath"]
t.pickupSounds=kronkSounds
t.fallSounds=["kronkFall"]

t.style = 'female'

###############  BONES  ##################

t = Appearance("Huesos Rosa")

t.colorTexture = "bonesColor"
t.colorMaskTexture = "bonesColorMask"

t.defaultColor = (0.6, 0.9, 1)
t.defaultHighlight = (0.6, 0.9, 1)

t.iconTexture = "bonesIcon"
t.iconMaskTexture = "bonesIconColorMask"

t.headModel =     "bonesHead"
t.torsoModel =    "bonesTorso"
t.pelvisModel =   "bonesPelvis"
t.upperArmModel = "bonesUpperArm"
t.foreArmModel =  "bonesForeArm"
t.handModel =     "bonesHand"
t.upperLegModel = "bonesUpperLeg"
t.lowerLegModel = "bonesLowerLeg"
t.toesModel =     "bonesToes"

bonesSounds =    ['bones1', 'bones2', 'bones3']
bonesHitSounds = ['bones1', 'bones2', 'bones3']

t.attackSounds = bonesSounds
t.jumpSounds = bonesSounds
t.impactSounds = bonesHitSounds
t.deathSounds=["bonesDeath"]
t.pickupSounds = bonesSounds
t.fallSounds=["bonesFall"]

t.style = 'pixie'

# Panda ###################################

t = Appearance("Panda")

t.colorTexture = "pandaColor"
t.colorMaskTexture = "pandaColorMask"

t.defaultColor = (1,1,1)
t.defaultHighlight = (0,0,0)

t.iconTexture = "pandaIcon"
t.iconMaskTexture = "pandaIconColorMask"

t.headModel =     "bearHead"
t.torsoModel =    "bearTorso"
t.pelvisModel =   "bearPelvis"
t.upperArmModel = "bearUpperArm"
t.foreArmModel =  "bearForeArm"
t.handModel =     "bearHand"
t.upperLegModel = "bearUpperLeg"
t.lowerLegModel = "bearLowerLeg"
t.toesModel =     "bearToes"

bearSounds =    ['bear1','bear2','bear3','bear4']
bearHitSounds = ['bearHit1','bearHit2']

t.attackSounds = bearSounds
t.jumpSounds = bearSounds
t.impactSounds = bearHitSounds
t.deathSounds=["bearDeath"]
t.pickupSounds = bearSounds
t.fallSounds=["bearFall"]

t.style = 'bear'

# S2059 ###################################
t = Appearance("SEBASTIAN2059")
t.colorTexture = "S2059Color"
t.colorMaskTexture = "S2059ColorMask"
t.defaultColor = (0,1,1)
#t.defaultHighlight = (1,0,0)
t.iconTexture = "S2059IconColor"
t.iconMaskTexture = "S2059IconMask"
t.headModel =     "S2059Head"
t.torsoModel =    "S2059Torso"
t.pelvisModel =   "zero"
t.upperArmModel = "S2059Arm"
t.foreArmModel =  "zero"
t.handModel =     "zero"
t.upperLegModel = "S2059Leg"
t.lowerLegModel = "zero"
t.toesModel =     "zero"  
agentSounds =    ['agent1','agent2','agent3','agent4']
agentHitSounds = ['agentHit1','agentHit2']
t.attackSounds = agentSounds
t.jumpSounds = agentSounds
t.impactSounds = agentHitSounds
t.deathSounds=["agentDeath"]
t.pickupSounds = agentSounds
t.fallSounds=["agentFall"]
t.style = 'agent'

###############  SPAZ   ##################
t = Appearance("Ice")

t.colorTexture = "powerupIceBombs"
t.colorMaskTexture = "bunnyColorMask"

t.iconTexture = "powerupIceBombs"
t.iconMaskTexture = "powerupIceBombs"

t.headModel = "powerup"
t.torsoModel = "neoSpazTorso"
t.pelvisModel = "neoSpazPelvis"
t.upperArmModel = "neoSpazUpperArm"
t.foreArmModel = "neoSpazForeArm"
t.handModel = "neoSpazHand"
t.upperLegModel = "neoSpazUpperLeg"
t.lowerLegModel = "neoSpazLowerLeg"
t.toesModel = "neoSpazToes"

t.jumpSounds=["spazJump01",
              "spazJump02",
              "spazJump03",
              "spazJump04"]
t.attackSounds=["spazAttack01",
                "spazAttack02",
                "spazAttack03",
                "spazAttack04"]
t.impactSounds=["spazImpact01",
                "spazImpact02",
                "spazImpact03",
                "spazImpact04"]
t.deathSounds=["spazDeath01"]
t.pickupSounds=["spazPickup01"]
t.fallSounds=["spazFall01"]

t.style = 'cyborg'

###############  SPAZ   ##################
t = Appearance("Health")

t.colorTexture = "powerupHealth"
t.colorMaskTexture = "bunnyColorMask"

t.iconTexture = "powerupHealth"
t.iconMaskTexture = "powerupHealth"

t.headModel = "powerup"
t.torsoModel = "neoSpazTorso"
t.pelvisModel = "neoSpazPelvis"
t.upperArmModel = "neoSpazUpperArm"
t.foreArmModel = "neoSpazForeArm"
t.handModel = "neoSpazHand"
t.upperLegModel = "neoSpazUpperLeg"
t.lowerLegModel = "neoSpazLowerLeg"
t.toesModel = "neoSpazToes"

t.jumpSounds=["spazJump01",
              "spazJump02",
              "spazJump03",
              "spazJump04"]
t.attackSounds=["spazAttack01",
                "spazAttack02",
                "spazAttack03",
                "spazAttack04"]
t.impactSounds=["spazImpact01",
                "spazImpact02",
                "spazImpact03",
                "spazImpact04"]
t.deathSounds=["spazDeath01"]
t.pickupSounds=["spazPickup01"]
t.fallSounds=["spazFall01"]

t.style = 'cyborg'

###############  SPAZ   ##################
t = Appearance("Sticky")

t.colorTexture = "powerupStickyBombs"
t.colorMaskTexture = "bunnyColorMask"

t.iconTexture = "powerupStickyBombs"
t.iconMaskTexture = "powerupStickyBombs"

t.headModel = "powerup"
t.torsoModel = "neoSpazTorso"
t.pelvisModel = "neoSpazPelvis"
t.upperArmModel = "neoSpazUpperArm"
t.foreArmModel = "neoSpazForeArm"
t.handModel = "neoSpazHand"
t.upperLegModel = "neoSpazUpperLeg"
t.lowerLegModel = "neoSpazLowerLeg"
t.toesModel = "neoSpazToes"

t.jumpSounds=["spazJump01",
              "spazJump02",
              "spazJump03",
              "spazJump04"]
t.attackSounds=["spazAttack01",
                "spazAttack02",
                "spazAttack03",
                "spazAttack04"]
t.impactSounds=["spazImpact01",
                "spazImpact02",
                "spazImpact03",
                "spazImpact04"]
t.deathSounds=["spazDeath01"]
t.pickupSounds=["spazPickup01"]
t.fallSounds=["spazFall01"]

t.style = 'cyborg'

###############  SPAZ   ##################
t = Appearance("Curse")

t.colorTexture = "powerupCurse"
t.colorMaskTexture = "bunnyColorMask"

t.iconTexture = "powerupCurse"
t.iconMaskTexture = "powerupCurse"

t.headModel = "powerup"
t.torsoModel = "neoSpazTorso"
t.pelvisModel = "neoSpazPelvis"
t.upperArmModel = "neoSpazUpperArm"
t.foreArmModel = "neoSpazForeArm"
t.handModel = "neoSpazHand"
t.upperLegModel = "neoSpazUpperLeg"
t.lowerLegModel = "neoSpazLowerLeg"
t.toesModel = "neoSpazToes"

t.jumpSounds=["spazJump01",
              "spazJump02",
              "spazJump03",
              "spazJump04"]
t.attackSounds=["spazAttack01",
                "spazAttack02",
                "spazAttack03",
                "spazAttack04"]
t.impactSounds=["spazImpact01",
                "spazImpact02",
                "spazImpact03",
                "spazImpact04"]
t.deathSounds=["spazDeath01"]
t.pickupSounds=["spazPickup01"]
t.fallSounds=["spazFall01"]

t.style = 'cyborg'

###############  SPAZ   ##################
t = Appearance("Shield")

t.colorTexture = "powerupShield"
t.colorMaskTexture = "bunnyColorMask"

t.iconTexture = "powerupShield"
t.iconMaskTexture = "powerupShield"

t.headModel = "powerup"
t.torsoModel = "neoSpazTorso"
t.pelvisModel = "neoSpazPelvis"
t.upperArmModel = "neoSpazUpperArm"
t.foreArmModel = "neoSpazForeArm"
t.handModel = "neoSpazHand"
t.upperLegModel = "neoSpazUpperLeg"
t.lowerLegModel = "neoSpazLowerLeg"
t.toesModel = "neoSpazToes"

t.jumpSounds=["spazJump01",
              "spazJump02",
              "spazJump03",
              "spazJump04"]
t.attackSounds=["spazAttack01",
                "spazAttack02",
                "spazAttack03",
                "spazAttack04"]
t.impactSounds=["spazImpact01",
                "spazImpact02",
                "spazImpact03",
                "spazImpact04"]
t.deathSounds=["spazDeath01"]
t.pickupSounds=["spazPickup01"]
t.fallSounds=["spazFall01"]

t.style = 'cyborg'

###############  SPAZ   ##################
t = Appearance("Punch")

t.colorTexture = "powerupPunch"
t.colorMaskTexture = "bunnyColorMask"

t.iconTexture = "powerupPunch"
t.iconMaskTexture = "powerupPunch"

t.headModel = "powerup"
t.torsoModel = "neoSpazTorso"
t.pelvisModel = "neoSpazPelvis"
t.upperArmModel = "neoSpazUpperArm"
t.foreArmModel = "neoSpazForeArm"
t.handModel = "neoSpazHand"
t.upperLegModel = "neoSpazUpperLeg"
t.lowerLegModel = "neoSpazLowerLeg"
t.toesModel = "neoSpazToes"

t.jumpSounds=["spazJump01",
              "spazJump02",
              "spazJump03",
              "spazJump04"]
t.attackSounds=["spazAttack01",
                "spazAttack02",
                "spazAttack03",
                "spazAttack04"]
t.impactSounds=["spazImpact01",
                "spazImpact02",
                "spazImpact03",
                "spazImpact04"]
t.deathSounds=["spazDeath01"]
t.pickupSounds=["spazPickup01"]
t.fallSounds=["spazFall01"]

t.style = 'cyborg'

###############  SPAZ   ##################
t = Appearance("Bomb")

t.colorTexture = "powerupBomb"
t.colorMaskTexture = "bunnyColorMask"

t.iconTexture = "powerupBomb"
t.iconMaskTexture = "powerupBomb"

t.headModel = "powerup"
t.torsoModel = "neoSpazTorso"
t.pelvisModel = "neoSpazPelvis"
t.upperArmModel = "neoSpazUpperArm"
t.foreArmModel = "neoSpazForeArm"
t.handModel = "neoSpazHand"
t.upperLegModel = "neoSpazUpperLeg"
t.lowerLegModel = "neoSpazLowerLeg"
t.toesModel = "neoSpazToes"

t.jumpSounds=["spazJump01",
              "spazJump02",
              "spazJump03",
              "spazJump04"]
t.attackSounds=["spazAttack01",
                "spazAttack02",
                "spazAttack03",
                "spazAttack04"]
t.impactSounds=["spazImpact01",
                "spazImpact02",
                "spazImpact03",
                "spazImpact04"]
t.deathSounds=["spazDeath01"]
t.pickupSounds=["spazPickup01"]
t.fallSounds=["spazFall01"]

t.style = 'cyborg'

###############  SPAZ   ##################
t = Appearance("LandMine")

t.colorTexture = "powerupLandMines"
t.colorMaskTexture = "bunnyColorMask"

t.iconTexture = "powerupLandMines"
t.iconMaskTexture = "powerupLandMines"

t.headModel = "powerup"
t.torsoModel = "neoSpazTorso"
t.pelvisModel = "neoSpazPelvis"
t.upperArmModel = "neoSpazUpperArm"
t.foreArmModel = "neoSpazForeArm"
t.handModel = "neoSpazHand"
t.upperLegModel = "neoSpazUpperLeg"
t.lowerLegModel = "neoSpazLowerLeg"
t.toesModel = "neoSpazToes"

t.jumpSounds=["spazJump01",
              "spazJump02",
              "spazJump03",
              "spazJump04"]
t.attackSounds=["spazAttack01",
                "spazAttack02",
                "spazAttack03",
                "spazAttack04"]
t.impactSounds=["spazImpact01",
                "spazImpact02",
                "spazImpact03",
                "spazImpact04"]
t.deathSounds=["spazDeath01"]
t.pickupSounds=["spazPickup01"]
t.fallSounds=["spazFall01"]

t.style = 'cyborg'

# Agent ###################################
t = Appearance("Impact")
t.colorTexture = "powerupImpactBombs"
t.colorMaskTexture = "impactBombColorLit"
t.defaultColor = (0.3, 0.3, 0.33)
t.defaultHighlight = (1, 0.5, 0.3)
t.iconTexture = "powerupImpactBombs"
t.iconMaskTexture = "powerupImpactBombs"
t.headModel =     "powerup"
t.torsoModel =    "agentTorso"
t.pelvisModel =   "agentPelvis"
t.upperArmModel = "agentUpperArm"
t.foreArmModel =  "agentForeArm"
t.handModel =     "agentHand"
t.upperLegModel = "agentUpperLeg"
t.lowerLegModel = "agentLowerLeg"
t.toesModel =     "agentToes"
agentSounds =    ['agent1', 'agent2', 'agent3', 'agent4']
agentHitSounds = ['agentHit1', 'agentHit2']
t.attackSounds = agentSounds
t.jumpSounds = agentSounds
t.impactSounds = agentHitSounds
t.deathSounds=["agentDeath"]
t.pickupSounds = agentSounds
t.fallSounds=["agentFall"]
t.style = 'cyborg'


###############  SPAZ   ##################
t = Appearance("Speed")

t.colorTexture = "powerupSpeed"
t.colorMaskTexture = "bunnyColorMask"

t.iconTexture = "powerupSpeed"
t.iconMaskTexture = "powerupSpeed"

t.headModel = "powerup"
t.torsoModel = "neoSpazTorso"
t.pelvisModel = "neoSpazPelvis"
t.upperArmModel = "neoSpazUpperArm"
t.foreArmModel = "neoSpazForeArm"
t.handModel = "neoSpazHand"
t.upperLegModel = "neoSpazUpperLeg"
t.lowerLegModel = "neoSpazLowerLeg"
t.toesModel = "neoSpazToes"

t.jumpSounds=["spazJump01","spazJump02","spazJump03","spazJump04"]
t.attackSounds=["spazAttack01","spazAttack02","spazAttack03","spazAttack04"]
t.impactSounds=["spazImpact01","spazImpact02","spazImpact03","spazImpact04"]
t.deathSounds=["spazDeath01"]
t.pickupSounds=["spazPickup01"]
t.fallSounds=["spazFall01"]

t.style = 'cyborg'
