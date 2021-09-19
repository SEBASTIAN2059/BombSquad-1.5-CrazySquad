import bs
import random
import bsUtils
import settings 

defaultPowerupInterval = 8000

class PowerupMessage(object):
    """
    category: Message Classes

    Tell something to get a powerup.
    This message is normally recieved by touching
    a bs.Powerup box.
    
    Attributes:
    
       powerupType
          The type of powerup to be granted (a string).
          See bs.Powerup.powerupType for available type values.

       sourceNode
          The node the powerup game from, or an empty bs.Node ref otherwise.
          If a powerup is accepted, a bs.PowerupAcceptMessage should be sent
          back to the sourceNode to inform it of the fact. This will generally
          cause the powerup box to make a sound and disappear or whatnot.
    """
    def __init__(self,powerupType,sourceNode=bs.Node(None)):
        """
        Instantiate with given values.
        See bs.Powerup.powerupType for available type values.
        """
        self.powerupType = powerupType
        self.sourceNode = sourceNode

class PowerupAcceptMessage(object):
    """
    category: Message Classes

    Inform a bs.Powerup that it was accepted.
    This is generally sent in response to a bs.PowerupMessage
    to inform the box (or whoever granted it) that it can go away.
    """
    pass

class _TouchedMessage(object):
    pass

class PowerupFactory(object):
    """
    category: Game Flow Classes
    
    Wraps up media and other resources used by bs.Powerups.
    A single instance of this is shared between all powerups
    and can be retrieved via bs.Powerup.getFactory().

    Attributes:

       model
          The bs.Model of the powerup box.

       modelSimple
          A simpler bs.Model of the powerup box, for use in shadows, etc.

       texBox
          Triple-bomb powerup bs.Texture.

       texPunch
          Punch powerup bs.Texture.

       texIceBombs
          Ice bomb powerup bs.Texture.

       texStickyBombs
          Sticky bomb powerup bs.Texture.

       texShield
          Shield powerup bs.Texture.

       texImpactBombs
          Impact-bomb powerup bs.Texture.

       texHealth
          Health powerup bs.Texture.

       texLandMines
          Land-mine powerup bs.Texture.

       texCurse
          Curse powerup bs.Texture.

       healthPowerupSound
          bs.Sound played when a health powerup is accepted.

       powerupSound
          bs.Sound played when a powerup is accepted.

       powerdownSound
          bs.Sound that can be used when powerups wear off.

       powerupMaterial
          bs.Material applied to powerup boxes.

       powerupAcceptMaterial
          Powerups will send a bs.PowerupMessage to anything they touch
          that has this bs.Material applied.
    """

    def __init__(self):
        """
        Instantiate a PowerupFactory.
        You shouldn't need to do this; call bs.Powerup.getFactory()
        to get a shared instance.
        """

        self._lastPowerupType = None

        self.model = bs.getModel("powerup")
        self.modelSimple = bs.getModel("powerupSimple")

        self.texBomb = bs.getTexture("powerupBomb")
        self.texPunch = bs.getTexture("powerupPunch")
        self.texIceBombs = bs.getTexture("powerupIceBombs")
        self.texStickyBombs = bs.getTexture("powerupStickyBombs")
        self.texShield = bs.getTexture("powerupShield")
        self.texImpactBombs = bs.getTexture("powerupImpactBombs")
        self.texHealth = bs.getTexture("powerupHealth")
        self.texLandMines = bs.getTexture("powerupLandMines")
        self.texCurse = bs.getTexture("powerupCurse")
        self.texLuckyBlock = bs.getTexture("powerupLuckyBlocks")
        self.texUS = bs.getTexture("powerupEspectralBombs")
        self.texCP = bs.getTexture("powerupSuicide")
        self.texDeathOrb = bs.getTexture("powerupMagicBombs")
        self.texSpeed = bs.getTexture("powerupSpeed")
        self.texTntBombs = bs.getTexture("powerupTntBombs")
        self.texIceImpact = bs.getTexture("powerupIceImpactBombs")
        self.texSonicBomb = bs.getTexture("powerupSonicBombs")
        self.texExtraLive = bs.getTexture("powerupExtraLive")
        self.texPowerupBomb = bs.getTexture("powerupFakePowerups")
        #self.texHappyBombs = bs.getTexture("logo")
        self.texPower = bs.getTexture("powerupPower")
        #self.texLongWayBombs = bs.getTexture("ouyaIcon")
        self.texBombJumping = bs.getTexture("powerupJumpBombs")
        self.texUpSticky = bs.getTexture("powerupUpStickyBombs")
        self.texElectricBomb = bs.getTexture("powerupElectricBombs")
        #self.texCurseBomb = bs.getTexture("eggTex3")
        self.texPowerupsLol = bs.getTexture("powerupTools")
        self.texGod = bs.getTexture("powerupInvincible")
        self.texIB = bs.getTexture("powerupInvisible")
        self.texBB = bs.getTexture("powerupBugBombs")
        self.texEgg = bs.getTexture("powerupEggBombs")
        self.texDirigida = bs.getTexture("powerupAimBombs")
        self.texShock = bs.getTexture("powerupShockBombs")

        self.healthPowerupSound = bs.getSound("healthPowerup")
        self.powerupSound = bs.getSound("powerup01")
        self.powerdownSound = bs.getSound("powerdown01")
        self.dropSound = bs.getSound("boxDrop")

        # material for powerups
        self.powerupMaterial = bs.Material()

        # material for anyone wanting to accept powerups
        self.powerupAcceptMaterial = bs.Material()

        # pass a powerup-touched message to applicable stuff
        self.powerupMaterial.addActions(
            conditions=(("theyHaveMaterial",self.powerupAcceptMaterial)),
            actions=(("modifyPartCollision","collide",True),
                     ("modifyPartCollision","physical",False),
                     ("message","ourNode","atConnect",_TouchedMessage())))

        # we dont wanna be picked up
        self.powerupMaterial.addActions(
            conditions=("theyHaveMaterial",
                        bs.getSharedObject('pickupMaterial')),
            actions=( ("modifyPartCollision","collide",False)))

        self.powerupMaterial.addActions(
            conditions=("theyHaveMaterial",
                        bs.getSharedObject('footingMaterial')),
            actions=(("impactSound",self.dropSound,0.5,0.1)))

        self._powerupDist = []
        for p,freq in getDefaultPowerupDistribution():
            for i in range(int(freq)):
                self._powerupDist.append(p)

    def getRandomPowerupType(self,forceType=None,excludeTypes=[]):
        """
        Returns a random powerup type (string).
        See bs.Powerup.powerupType for available type values.

        There are certain non-random aspects to this; a 'curse' powerup,
        for instance, is always followed by a 'health' powerup (to keep things
        interesting). Passing 'forceType' forces a given returned type while
        still properly interacting with the non-random aspects of the system
        (ie: forcing a 'curse' powerup will result
        in the next powerup being health).
        """
        import weakref
        try:
            self._gamemode = bs.getActivity().getName()
            self._map = bs.getActivity()._map.getName()
        except Exception:
            self._gamemode = None
            self._map = None
		
        if self._gamemode == 'Onslaught' or self._gamemode == 'Football' or self._gamemode == 'Ninja Fight' or self._gamemode == 'Ninja Fight' or self._gamemode == 'Runaround' or self._gamemode == 'The Last Stand':
            coopDisable = ['luckyBlock','powerupsLol','magicBomb','iceImpact','endBomb','upSticky',
           			   'electricBomb','cyp','power','god','extraLive','powerupBomb','bombJumping','speed','tntBombs',
           			   'eggBomb','shockBomb','espectralBomb','dirigida','invisible','bugBomb','shield']
        else:
            coopDisable = ['shieldCoop']
                    
        if (self._gamemode == 'Race' 
            or self._gamemode == 'Assault' 
            or self._gamemode == 'Hockey' 
            or self._gamemode == 'Chosen One'
            or self._map == 'Happy Thoughts'):
            speedDisable = ['speed']
        else:
            speedDisable = []
            
        #if (isinstance(bs.getSession(),bs.FreeForAllSession)
            #or isinstance(bs.getSession(),bs.TeamsSession)):
            #shieldCDisable=['shieldCoop']
        #else:
            #shieldCDisable=[]
                   
        if (self._gamemode == 'Balonmano' 
            or self._gamemode == 'Futbol Soccer' 
            or self._gamemode == 'Hockey' 
            or self._gamemode == 'Basketball'):
            #or self._map == 'Happy Thoughts'):
            dangerDisable = ['magicBomb','luckyBlock']
        else:
            dangerDisable = []
            
        if forceType:
            t = forceType
        else:
            # if the last one was a curse, make this one a health to
            # provide some hope
            if self._lastPowerupType == 'curse':
                t = 'health'
            elif self._lastPowerupType == 'cyp':
                t = 'extraLive'
            else:
                while True:
                    t = self._powerupDist[
                        random.randint(0, len(self._powerupDist)-1)]
                    if t not in excludeTypes and t not in coopDisable and t not in speedDisable and t not in dangerDisable:
                        break
        self._lastPowerupType = t
        return t


def getDefaultPowerupDistribution():
    return (('tripleBombs',3),
            ('iceBombs',3),
            ('punch',3),
            ('impactBombs',3),
            ('landMines',2),
            ('stickyBombs',3),
            ('shield',2),
            ('health',2),
            ('curse',1),
            ('luckyBlock',4),
            ('powerupsLol',1),
            ('magicBomb',1),
            ('iceImpact',1),
            ('endBomb',2),
            ('upSticky',2),
            ('electricBomb',2),
            ('cyp',1),
            ('power',2),
            ('god',1),
            ('extraLive',1),
            ('powerupBomb',2),
            ('bombJumping',2),
            ('speed',2),
            ('tntBombs',2),
            ('eggBomb',3),
            ('shockBomb',2),
            ('espectralBomb',1),
            ('dirigida',2),
            ('shieldCoop',2),
            ('bugBomb',2))

class Powerup(bs.Actor):
    """
    category: Game Flow Classes

    A powerup box.
    This will deliver a bs.PowerupMessage to anything that touches it
    which has the bs.PowerupFactory.powerupAcceptMaterial applied.

    Attributes:

       powerupType
          The string powerup type.  This can be 'tripleBombs', 'punch',
          'iceBombs', 'impactBombs', 'landMines', 'stickyBombs', 'shield',
          'health', or 'curse'.

       node
          The 'prop' bs.Node representing this box.
    """

    def __init__(self,position=(0,1,0),powerupType='tripleBombs',expire=True,decorate=True, shield=False):
        """
        Create a powerup-box of the requested type at the requested position.

        see bs.Powerup.powerupType for valid type strings.
        """
        
        bs.Actor.__init__(self)

        factory = self.getFactory()
        self.powerupType = powerupType;
        self._powersGiven = False
        
        color = (1,1,1)

        if powerupType == 'tripleBombs': 
            tex = factory.texBomb
            color = (1.2,1.2,1)
        elif powerupType == 'punch': 
            tex = factory.texPunch
            color = (1.2,1.2,1)
        elif powerupType == 'iceBombs': 
            tex = factory.texIceBombs
            color = (1.2,1.2,1)
        elif powerupType == 'impactBombs': 
            tex = factory.texImpactBombs
            color = (1.2,1.2,1)
        elif powerupType == 'landMines': 
            tex = factory.texLandMines
            color = (1.2,1.2,1)
        elif powerupType == 'stickyBombs': 
            tex = factory.texStickyBombs
            color = (1.2,1.2,1)
        elif powerupType == 'luckyBlock': 
            tex = factory.texLuckyBlock
            color = (1.2,1.2,1)
        elif powerupType == 'shield': 
            tex = factory.texShield
            color = (1.2,1.2,1)
        elif powerupType == 'health': 
            tex = factory.texHealth
            color = (1.2,1.2,1)
        elif powerupType == 'curse': 
            tex = factory.texCurse
            color = (1.2,1.2,1)
        elif powerupType == 'rm': 
            tex = factory.texRM
            color = (1.2,1.2,1)
        elif powerupType == 'espectralBomb': 
            tex = factory.texUS
            color = (1.2,1.2,1)
        elif powerupType == 'cyp': 
            tex = factory.texCP
            color = (1.2,1.2,1)
        elif powerupType == 'tntBombs': 
            tex = factory.texTntBombs
            color = (1.2,1.2,1)
        elif powerupType == 'magicBomb': 
            tex = factory.texDeathOrb
            color = (1.2,1.2,1)
        elif powerupType == 'speed': 
            tex = factory.texSpeed
            color = (1.2,1.2,1)
        elif powerupType == 'iceImpact': 
            tex = factory.texIceImpact
            color = (1.2,1.2,1)
        elif powerupType == 'endBomb': 
            tex = factory.texSonicBomb
            color = (1.2,1.2,1)
        elif powerupType == 'extraLive': 
            tex = factory.texExtraLive
            color = (1.2,1.2,1)
        elif powerupType == 'powerupBomb': 
            tex = factory.texPowerupBomb
            color = (1.2,1.2,1)
        elif powerupType == 'power': 
            tex = factory.texPower
            color = (1.2,1.2,1)
        elif powerupType == 'bombJumping': 
            tex = factory.texBombJumping
            color = (1.2,1.2,1)
        elif powerupType == 'upSticky': 
            tex = factory.texUpSticky
            color = (1.2,1.2,1)
        elif powerupType == 'electricBomb': 
            tex = factory.texElectricBomb
            color = (1.2,1.2,1)
        elif powerupType == 'powerupsLol': 
            tex = factory.texPowerupsLol
            color = (1.2,1.2,1)
        elif powerupType == 'god': 
            tex = factory.texGod
            color = (1.2,1.2,1)
        elif powerupType == 'shieldCoop': 
            tex = factory.texShield
            color = (1.2,1.2,1)
        elif powerupType == 'bugBomb': 
            tex = factory.texBB
            color = (1.2,1.2,1)
        elif powerupType == 'eggBomb': 
            tex = factory.texEgg
            color = (1.2,1.2,1)
        elif powerupType == 'shockBomb': 
            tex = factory.texShock
            color = (1.2,1.2,1)
        elif powerupType == 'dirigida': 
            tex = factory.texDirigida
            color = (1.2,1.2,1)
        else: raise Exception("invalid powerupType: "+str(powerupType))

        if len(position) != 3: raise Exception("expected 3 floats for position")
        
        self.node = bs.newNode(
            'prop',
            delegate=self,
            attrs={'body':'box',
                   'position':position,
                   'model':factory.model,
                   'lightModel':factory.modelSimple,
                   'shadowSize':0.5,
                   'colorTexture':tex,
                   'reflection':'powerup',
                   'reflectionScale':[1.0],
                   'materials':(factory.powerupMaterial,
                                bs.getSharedObject('objectMaterial'))})
                                
        # animate in..
        curve = bs.animate(self.node,"modelScale",{0:0,140:1.6,200:1})
        bs.gameTimer(200,curve.delete)
        
        if settings.night == True:
            self.shield = bs.newNode('light', owner=self.node,
                                          attrs={'color':(1,1,1), 'volumeIntensityScale': 1.0,'intensity':0.6,'radius':0.25})
            self.node.connectAttr('position', self.shield, 'position')                                              
        if settings.night == False:
            None

        self.decorate = decorate

        if expire:
            bs.gameTimer(defaultPowerupInterval-2500,
                         bs.WeakCall(self._startFlashing))
            bs.gameTimer(defaultPowerupInterval-1000,
                         bs.WeakCall(self.handleMessage, bs.DieMessage()))

    @classmethod
    def getFactory(cls):
        """
        Returns a shared bs.PowerupFactory object, creating it if necessary.
        """
        activity = bs.getActivity()
        if activity is None: raise Exception("no current activity")
        try: return activity._sharedPowerupFactory
        except Exception:
            f = activity._sharedPowerupFactory = PowerupFactory()
            return f
            
    def _startFlashing(self):
        if self.node.exists(): self.node.flashing = True

        
    def handleMessage(self, msg):
        self._handleMessageSanityCheck()

        if isinstance(msg, PowerupAcceptMessage):
            factory = self.getFactory()
            if self.powerupType == 'health':
                bs.playSound(factory.healthPowerupSound, 3,
                             position=self.node.position)
            bs.playSound(factory.powerupSound, 3, position=self.node.position)
            self._powersGiven = True
            bs.statAdd('Powerup Total')
            self.handleMessage(bs.DieMessage())

        elif isinstance(msg, _TouchedMessage):
            if not self._powersGiven:
                node = bs.getCollisionInfo("opposingNode")
                if node is not None and node.exists():
                    node.handleMessage(PowerupMessage(self.powerupType,
                                                      sourceNode=self.node))

        elif isinstance(msg, bs.DieMessage):
            if self.node.exists():
                if (msg.immediate):
                    self.node.delete()
                else:
                    curve = bs.animate(self.node, "modelScale", {0:1,100:0})
                    bs.gameTimer(100, self.node.delete)

        elif isinstance(msg ,bs.OutOfBoundsMessage):
            self.handleMessage(bs.DieMessage())

        elif isinstance(msg, bs.HitMessage):
            # dont die on punches (thats annoying)
            if msg.hitType != 'punch':
                self.handleMessage(bs.DieMessage())
        else:
            bs.Actor.handleMessage(self, msg)
