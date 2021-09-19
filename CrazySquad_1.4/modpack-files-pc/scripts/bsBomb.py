import bs
import bsUtils
from bsVector import Vector
import random
import weakref
import bsSpaz


class BombFactory(object):
    """
    category: Game Flow Classes

    Wraps up media and other resources used by bs.Bombs
    A single instance of this is shared between all bombs
    and can be retrieved via bs.Bomb.getFactory().

    Attributes:

       bombModel
          The bs.Model of a standard or ice bomb.

       stickyBombModel
          The bs.Model of a sticky-bomb.

       impactBombModel
          The bs.Model of an impact-bomb.

       landMinModel
          The bs.Model of a land-mine.

       tntModel
          The bs.Model of a tnt box.

       regularTex
          The bs.Texture for regular bombs.

       iceTex
          The bs.Texture for ice bombs.

       stickyTex
          The bs.Texture for sticky bombs.

       impactTex
          The bs.Texture for impact bombs.

       impactLitTex
          The bs.Texture for impact bombs with lights lit.

       landMineTex
          The bs.Texture for land-mines.

       landMineLitTex
          The bs.Texture for land-mines with the light lit.

       tntTex
          The bs.Texture for tnt boxes.

       hissSound
          The bs.Sound for the hiss sound an ice bomb makes.

       debrisFallSound
          The bs.Sound for random falling debris after an explosion.

       woodDebrisFallSound
          A bs.Sound for random wood debris falling after an explosion.

       explodeSounds
          A tuple of bs.Sounds for explosions.

       freezeSound
          A bs.Sound of an ice bomb freezing something.

       fuseSound
          A bs.Sound of a burning fuse.

       activateSound
          A bs.Sound for an activating impact bomb.

       warnSound
          A bs.Sound for an impact bomb about to explode due to time-out.

       bombMaterial
          A bs.Material applied to all bombs.

       normalSoundMaterial
          A bs.Material that generates standard bomb noises on impacts, etc.

       stickyMaterial
          A bs.Material that makes 'splat' sounds and makes collisions softer.

       landMineNoExplodeMaterial
          A bs.Material that keeps land-mines from blowing up.
          Applied to land-mines when they are created to allow land-mines to
          touch without exploding.

       landMineBlastMaterial
          A bs.Material applied to activated land-mines that causes them to
          explode on impact.

       impactBlastMaterial
          A bs.Material applied to activated impact-bombs that causes them to
          explode on impact.

       blastMaterial
          A bs.Material applied to bomb blast geometry which triggers impact
          events with what it touches.

       dinkSounds
          A tuple of bs.Sounds for when bombs hit the ground.

       stickyImpactSound
          The bs.Sound for a squish made by a sticky bomb hitting something.

       rollSound
          bs.Sound for a rolling bomb.
    """

    def getRandomExplodeSound(self):
        'Return a random explosion bs.Sound from the factory.'
        return self.explodeSounds[random.randrange(len(self.explodeSounds))]

    def __init__(self):
        """
        Instantiate a BombFactory.
        You shouldn't need to do this; call bs.Bomb.getFactory() to get a
        shared instance.
        """

        self.bombModel = bs.getModel('bomb')
        self.stickyBombModel = bs.getModel('bombSticky')
        self.impactBombModel = bs.getModel('impactBomb')
        self.eggBombModel = bs.getModel('egg')
        self.landMineModel = bs.getModel('landMine')
        self.powerupBombModel = bs.getModel('powerup')
        self.powerupBombModelS = bs.getModel('powerupSimple')
        self.tntModel = bs.getModel('tnt')
        self.iceDirigidaModel = bs.getModel('tnt')

        self.regularTex = bs.getTexture('bombColor')
        self.iceTex = bs.getTexture('bombColorIce')
        self.stickyTex = bs.getTexture('bombStickyColor')
        self.eggTex = bs.getTexture('eggTex1')
        self.egg2Tex = bs.getTexture('eggTex2')
        self.egg3Tex = bs.getTexture('eggTex3')
        self.impactTex = bs.getTexture('impactBombColor')
        self.impactLitTex = bs.getTexture('impactBombColorLit')
        self.landMineTex = bs.getTexture('landMine')
        self.landMineLitTex = bs.getTexture('landMineLit')
        self.cube1Tex = bs.getTexture('powerupImpactBombs')
        self.cube2Tex = bs.getTexture('powerupPunch')
        self.cube3Tex = bs.getTexture('powerupIceBombs')
        self.cube4Tex = bs.getTexture('powerupShield')
        self.cube5Tex = bs.getTexture('powerupHealth')
        self.cube6Tex = bs.getTexture('powerupCurse')
        self.cube7Tex = bs.getTexture('powerupStickyBombs')
        self.cube8Tex = bs.getTexture('powerupBomb')
        self.cube9Tex = bs.getTexture('powerupLandMines')
        self.tntTex = bs.getTexture('tnt')
        self.endBombTex = bs.getTexture('ouyaUButton')
        self.saltarinaTex = bs.getTexture('fontExtras2')
        self.crazyBombTex = bs.getTexture('achievementEmpty')
        self.dirigidaTex = bs.getTexture('bg')
        self.iceDirigidaTex = bs.getTexture('ouyaUButton')

        self.hissSound = bs.getSound('hiss')
        self.debrisFallSound = bs.getSound('debrisFall')
        self.woodDebrisFallSound = bs.getSound('woodDebrisFall')

        self.explodeSounds = (bs.getSound('explosion01'),
                              bs.getSound('explosion02'),
                              bs.getSound('explosion03'),
                              bs.getSound('explosion04'),
                              bs.getSound('explosion05'))

        self.freezeSound = bs.getSound('freeze')
        self.fuseSound = bs.getSound('fuse01')
        self.activateSound = bs.getSound('activateBeep')
        self.warnSound = bs.getSound('warnBeep')

        # set up our material so new bombs dont collide with objects
        # that they are initially overlapping
        self.bombMaterial = bs.Material()
        self.normalSoundMaterial = bs.Material()
        self.stickyMaterial = bs.Material()

        self.bombMaterial.addActions(
            conditions=((('weAreYoungerThan',100),
                         'or',('theyAreYoungerThan',100)),
                        'and',('theyHaveMaterial',
                               bs.getSharedObject('objectMaterial'))),
            actions=(('modifyNodeCollision','collide',False)))

        # we want pickup materials to always hit us even if we're currently not
        # colliding with their node (generally due to the above rule)
        self.bombMaterial.addActions(
            conditions=('theyHaveMaterial',
                        bs.getSharedObject('pickupMaterial')),
            actions=(('modifyPartCollision','useNodeCollide', False)))
        
        self.bombMaterial.addActions(actions=('modifyPartCollision',
                                              'friction', 0.3))

        self.landMineNoExplodeMaterial = bs.Material()
        self.landMineBlastMaterial = bs.Material()
        self.landMineBlastMaterial.addActions(
            conditions=(
                ('weAreOlderThan',200),
                 'and', ('theyAreOlderThan',200),
                 'and', ('evalColliding',),
                 'and', (('theyDontHaveMaterial',
                          self.landMineNoExplodeMaterial),
                         'and', (('theyHaveMaterial',
                                  bs.getSharedObject('objectMaterial')),
                                 'or',('theyHaveMaterial',
                                       bs.getSharedObject('playerMaterial'))))),
            actions=(('message', 'ourNode', 'atConnect', ImpactMessage())))
        
        self.impactBlastMaterial = bs.Material()
        self.impactBlastMaterial.addActions(
            conditions=(('weAreOlderThan', 200),
                        'and', ('theyAreOlderThan',200),
                        'and', ('evalColliding',),
                        'and', (('theyHaveMaterial',
                                 bs.getSharedObject('footingMaterial')),
                               'or',('theyHaveMaterial',
                                     bs.getSharedObject('objectMaterial')))),
            actions=(('message','ourNode','atConnect',ImpactMessage())))

        self.blastMaterial = bs.Material()
        self.blastMaterial.addActions(
            conditions=(('theyHaveMaterial',
                         bs.getSharedObject('objectMaterial'))),
            actions=(('modifyPartCollision','collide',True),
                     ('modifyPartCollision','physical',False),
                     ('message','ourNode','atConnect',ExplodeHitMessage())))

        self.dinkSounds = (bs.getSound('bombDrop01'),
                           bs.getSound('bombDrop02'))
        self.stickyImpactSound = bs.getSound('stickyImpact')
        self.rollSound = bs.getSound('bombRoll01')

        # collision sounds
        self.normalSoundMaterial.addActions(
            conditions=('theyHaveMaterial',
                        bs.getSharedObject('footingMaterial')),
            actions=(('impactSound',self.dinkSounds,2,0.8),
                     ('rollSound',self.rollSound,3,6)))

        self.stickyMaterial.addActions(
            actions=(('modifyPartCollision','stiffness',0.1),
                     ('modifyPartCollision','damping',1.0)))

        self.stickyMaterial.addActions(
            conditions=(('theyHaveMaterial',
                         bs.getSharedObject('playerMaterial')),
                        'or', ('theyHaveMaterial',
                               bs.getSharedObject('footingMaterial'))),
            actions=(('message','ourNode','atConnect',SplatMessage())))

class SplatMessage(object):
    pass

class ExplodeMessage(object):
    pass

class ImpactMessage(object):
    """ impact bomb touched something """
    pass

class ArmMessage(object):
    pass

class WarnMessage(object):
    pass

class ExplodeHitMessage(object):
    "Message saying an object was hit"
    def __init__(self):
        pass

class Blast(bs.Actor):
    """
    category: Game Flow Classes

    An explosion, as generated by a bs.Bomb.
    """
    def __init__(self, position=(0,1,0), velocity=(0,0,0), blastRadius=2.0,
                 blastType="normal", sourcePlayer=None, hitType='explosion',
                 hitSubType='normal'):
        """
        Instantiate with given values.
        """
        bs.Actor.__init__(self)
        
        factory = Bomb.getFactory()

        self.blastType = blastType
        self.sourcePlayer = sourcePlayer

        self.hitType = hitType;
        self.hitSubType = hitSubType;

        # blast radius
        self.radius = blastRadius

        # set our position a bit lower so we throw more things upward
        self.node = bs.newNode('region', delegate=self, attrs={
            'position':(position[0], position[1]-0.1, position[2]),
            'scale':(self.radius,self.radius,self.radius),
            'type':'sphere',
            'materials':(factory.blastMaterial,
                         bs.getSharedObject('attackMaterial'))})

        bs.gameTimer(50, self.node.delete)

        # throw in an explosion and flash
        explosion = bs.newNode("explosion", attrs={
            'position':position,
            'velocity':(velocity[0],max(-1.0,velocity[1]),velocity[2]),
            'radius':self.radius,
            'big':(self.blastType == 'tnt')})
        if self.blastType == "ice":
            explosion.color = (0, 0.05, 0.4)
            
        if self.blastType == "espectralBomb":
            explosion.color = (1,1,1)
            
        if self.blastType == "mostro":
            explosion.color = (0,0,0)
            
        if self.blastType == "BdM":
            explosion.color = (0,0,0.2)
            
        if self.blastType == "BdV":
            explosion.color = (1,0,0)
            
        if self.blastType == "magicBomb":
            explosion.color = (0.5,0,0.7)
            
        if self.blastType == "iceImpact":
            explosion.color = (1,1,1)
            
        if self.blastType == "menu":
            explosion.color = random.choice([(1*40,0,0),(0,1*20,0),(0,0,1*20),(1*20,1*20,0),(0,1*20,1*20),(1*20,0,1*20)])
            
        if self.blastType == "luckyBomb":
            explosion.color = (0,0,0)
            
        if self.blastType == "endBomb":
            explosion.color = (1,0.3,0.4)
            
        if self.blastType == "sticky":
            explosion.color = (0,1,0)
            
        if self.blastType == "landMine":
            explosion.color = (0,0.5,0.1)
            
        if self.blastType == "powerupBomb":
            explosion.color = random.choice([(1*40,0,0),(0,1*20,0),(0,0,1*20),(1*20,1*20,0),(0,1*20,1*20),(1*20,0,1*20)])
            
        if self.blastType == "impact":
            explosion.color = (0.3,0,0)
            
        if self.blastType == "electric":
            explosion.color = (0,0,0.2)
            
        if self.blastType == "bugBomb":
            explosion.color = (1*9,0,1*9)
            
        if self.blastType == "saltarina":
            explosion.color = (random.random(),random.random(),random.random())

        bs.gameTimer(1000,explosion.delete)

        if self.blastType != 'ice':
            bs.emitBGDynamics(position=position, velocity=velocity,
                              count=int(1.0+random.random()*4),
                              emitType='tendrils',tendrilType='thinSmoke')
        bs.emitBGDynamics(
            position=position, velocity=velocity,
            count=int(4.0+random.random()*4), emitType='tendrils',
            tendrilType='ice' if self.blastType == 'ice' else 'smoke')
        bs.emitBGDynamics(
            position=position, emitType='distortion',
            spread=1.0 if self.blastType == 'tnt' else 2.0)
        
        # and emit some shrapnel..
        if self.blastType == 'ice':
            def _doEmit():
                bs.emitBGDynamics(position=position, velocity=velocity,
                                  count=30, spread=2.0, scale=0.4,
                                  chunkType='ice', emitType='stickers');
            bs.gameTimer(50, _doEmit) # looks better if we delay a bit
            

        elif self.blastType == 'sticky':
            def _doEmit():
                bs.emitBGDynamics(position=position, velocity=velocity,
                                  count=int(4.0+random.random()*8),
                                  spread=0.7,chunkType='slime');
                bs.emitBGDynamics(position=position, velocity=velocity,
                                  count=int(4.0+random.random()*8), scale=0.5,
                                  spread=0.7,chunkType='slime');
                bs.emitBGDynamics(position=position, velocity=velocity,
                                  count=15, scale=0.6, chunkType='slime',
                                  emitType='stickers');
                bs.emitBGDynamics(position=position, velocity=velocity,
                                  count=20, scale=0.7, chunkType='spark',
                                  emitType='stickers');
                bs.emitBGDynamics(position=position, velocity=velocity,
                                  count=int(6.0+random.random()*12),
                                  scale=0.8, spread=1.5,chunkType='spark');
            bs.gameTimer(50,_doEmit) # looks better if we delay a bit

        elif self.blastType == 'impact': # regular bomb shrapnel
            def _doEmit():
                bs.emitBGDynamics(position=position, velocity=velocity,
                                  count=int(4.0+random.random()*8), scale=0.8,
                                  chunkType='metal');
                bs.emitBGDynamics(position=position, velocity=velocity,
                                  count=int(4.0+random.random()*8), scale=0.4,
                                  chunkType='metal');
                bs.emitBGDynamics(position=position, velocity=velocity,
                                  count=20, scale=0.7, chunkType='spark',
                                  emitType='stickers');
                bs.emitBGDynamics(position=position, velocity=velocity,
                                  count=int(8.0+random.random()*15), scale=0.8,
                                  spread=1.5, chunkType='spark');
            bs.gameTimer(50,_doEmit) # looks better if we delay a bit

        else: # regular or land mine bomb shrapnel
            def _doEmit():
                if self.blastType != 'tnt':
                    bs.emitBGDynamics(position=position, velocity=velocity,
                                      count=int(4.0+random.random()*8),
                                      chunkType='rock');
                    bs.emitBGDynamics(position=position, velocity=velocity,
                                      count=int(4.0+random.random()*8),
                                      scale=0.5,chunkType='rock');
                bs.emitBGDynamics(position=position, velocity=velocity,
                                  count=30,
                                  scale=1.0 if self.blastType=='tnt' else 0.7,
                                  chunkType='spark', emitType='stickers');
                bs.emitBGDynamics(position=position, velocity=velocity,
                                  count=int(18.0+random.random()*20),
                                  scale=1.0 if self.blastType == 'tnt' else 0.8,
                                  spread=1.5, chunkType='spark');

                # tnt throws splintery chunks
                if self.blastType == 'tnt':
                    def _emitSplinters():
                        bs.emitBGDynamics(position=position, velocity=velocity,
                                          count=int(20.0+random.random()*25),
                                          scale=0.8, spread=1.0,
                                          chunkType='splinter');
                    bs.gameTimer(10,_emitSplinters)
                
                # every now and then do a sparky one
                if self.blastType == 'tnt' or random.random() < 0.1:
                    def _emitExtraSparks():
                        bs.emitBGDynamics(position=position, velocity=velocity,
                                          count=int(10.0+random.random()*20),
                                          scale=0.8, spread=1.5,
                                          chunkType='spark');
                    bs.gameTimer(20,_emitExtraSparks)
                        
            bs.gameTimer(50,_doEmit) # looks better if we delay a bit

        light = bs.newNode('light', attrs={
            'position':position,
            'volumeIntensityScale': 10.0,
            'color': ((0.6, 0.6, 1.0) if self.blastType == 'ice'
                      else (1, 0.3, 0.1))})

        s = random.uniform(0.6,0.9)
        scorchRadius = lightRadius = self.radius
        if self.blastType == 'tnt':
            lightRadius *= 1.4
            scorchRadius *= 1.15
            s *= 3.0

        iScale = 1.6
        bsUtils.animate(light,"intensity", {
            0:2.0*iScale, int(s*20):0.1*iScale,
            int(s*25):0.2*iScale, int(s*50):17.0*iScale, int(s*60):5.0*iScale,
            int(s*80):4.0*iScale, int(s*200):0.6*iScale,
            int(s*2000):0.00*iScale, int(s*3000):0.0})
        bsUtils.animate(light,"radius", {
            0:lightRadius*0.2, int(s*50):lightRadius*0.55,
            int(s*100):lightRadius*0.3, int(s*300):lightRadius*0.15,
            int(s*1000):lightRadius*0.05})
        bs.gameTimer(int(s*3000),light.delete)

        # make a scorch that fades over time
        scorch = bs.newNode('scorch', attrs={
            'position':position,
            'size':scorchRadius*0.5,
            'big':(self.blastType == 'tnt')})
        if self.blastType == 'ice':
            scorch.color = (1,1,1.5)
            
        if self.blastType == 'iceImpact':
            scorch.color = (0,0.7,1.2)
            
        if self.blastType == 'menu':
            scorch.color = (random.random(),random.random(),random.random())
            
        if self.blastType == 'luckyBomb':
            scorch.color = (0,0,0)
            
        if self.blastType == 'endBomb':
            scorch.color = (0,0.2,0.7)
            
        if self.blastType == 'espectralBomb':
            scorch.color = (10*9,10*9,10*9)
            
        if self.blastType == 'mostro':
            scorch.color = (1,0.5,0)
            
        if self.blastType == 'BdM':
            scorch.color = (0,0,0.2)
            
        if self.blastType == 'BdV':
            scorch.color = (10,0,0)
            
        if self.blastType == 'magicBomb':
            scorch.color = (0.5,0,0.7)
            
        if self.blastType == 'sticky':
            scorch.color = (0,1,0.1)
            
        if self.blastType == 'landMine':
            scorch.color = (0,0.5,0.1)
            
        if self.blastType == 'powerupBomb':
            scorch.color = (0.5,0.5,0.5)
            
        if self.blastType == 'impact':
            scorch.color = (0.3,0,0)
            
        if self.blastType == 'electric':
            scorch.color = (0,0,0.2)
            
        if self.blastType == 'bugBomb':
            scorch.color = (1,0,1*4)
            
        if self.blastType == 'saltarina':
            scorch.color = (random.random(),random.random(),random.random())

        bsUtils.animate(scorch,"presence",{3000:1, 63000:0})
        bs.gameTimer(63000,scorch.delete)

        if self.blastType == 'ice':
            bs.playSound(factory.hissSound,position=light.position)
            
        p = light.position
        bs.playSound(factory.getRandomExplodeSound(),position=p)
        bs.playSound(factory.debrisFallSound,position=p)

        if self.blastType == 'menu':
            bs.shakeCamera(intensity=0)
        else:
        	#bs.shakeCamera(intensity=5.0 if self.blastType == 'tnt' else 1.0)
            bs.shakeCamera(intensity=0)

        # tnt is more epic..
        if self.blastType == 'tnt':
            bs.playSound(factory.getRandomExplodeSound(),position=p)
            def _extraBoom():
                bs.playSound(factory.getRandomExplodeSound(),position=p)
            bs.gameTimer(250,_extraBoom)
            def _extraDebrisSound():
                bs.playSound(factory.debrisFallSound,position=p)
                bs.playSound(factory.woodDebrisFallSound,position=p)
            bs.gameTimer(400,_extraDebrisSound)
            
    #Hl!
    #Esto es para que spawnee un bot al azar.
    def _getRandomBotType(self):
        bt = [bs.BomberBot,
                  bs.ToughGuyBot,
                  bs.ChickBot,
                  bs.PirateBot,
                  bs.NinjaBot,
                  bs.MelBot,
                  bs.BunnyBot,
                  bs.BomberBot,
                  bs.PascalBot,
                  bs.OsoMatonBot,
                  bs.FrostyBotPro,
                  bs.NeonBot,
                  bs.WizardBotPro,
                  bs.BearBotPro]
        return (random.choice(bt))

    def handleMessage(self, msg):
        self._handleMessageSanityCheck()
        
        if isinstance(msg, bs.DieMessage):
            self.node.delete()

        elif isinstance(msg, ExplodeHitMessage):
            node = bs.getCollisionInfo("opposingNode")
            if node is not None and node.exists():
                t = self.node.position

                # new
                mag = 2000.0
                if self.blastType == 'ice': mag *= 0.5
                elif self.blastType == 'crazyBomb': mag *= 0.3
                elif self.blastType == 'landMine': mag *= 2.5
                elif self.blastType == 'powerupBomb': mag *= 1.0
                elif self.blastType == 'espectralBomb': mag *= 0.8
                elif self.blastType == 'party': mag *= 0
                elif self.blastType == 'fireBomb': mag *= 0.4
                elif self.blastType == 'mostro': mag *= 1
                elif self.blastType == 'BdM': mag *= 0.1
                elif self.blastType == 'BdV': mag *= 0
                elif self.blastType == 'upSticky': mag *= 4
                elif self.blastType == 'magicBomb': mag *= 40
                elif self.blastType == 'iceImpact': mag *= 0.5
                elif self.blastType == 'shockBomb': mag *= 0.7
                elif self.blastType == 'eggBomb': mag *= 0.1
                elif self.blastType == 'menu': mag *= 0
                elif self.blastType == 'tnt': mag *= 2.0
                elif self.blastType == 'saltarina': mag *= 1.0
                elif self.blastType == 'electric': mag *= 0.5
                elif self.blastType == 'bugBomb': mag *= 0.3
                elif self.blastType == 'endBomb': mag *= 0
                elif self.blastType == 'luckyBomb': mag *= 0
                elif self.blastType == 'dirigida': mag *= 2.0
                elif self.blastType == 'iceDirigida': mag *= 0.5

                node.handleMessage(bs.HitMessage(
                    pos=t,
                    velocity=(0,0,0),
                    magnitude=mag,
                    hitType=self.hitType,
                    hitSubType=self.hitSubType,
                    radius=self.radius,
                    sourcePlayer=self.sourcePlayer))
                if self.blastType == "ice":
                    bs.playSound(Bomb.getFactory().freezeSound, 10, position=t)
                    node.handleMessage(bs.FreezeMessage())
                elif self.blastType == "espectralBomb":    
                	node.handleMessage(bs.EspectralMessage())
                	#node.handleMessage(bs.PowerupMessage(powerupType = 'paraEspectral'))
                elif self.blastType == "fireBomb":          
                	node.handleMessage(bs.PowerupMessage(powerupType = 'palFire'))
                elif self.blastType == "crazyBomb":          
                	bsUtils.PopupText("Todos Mueren\nNadie sobrevive?",color=(1,1,1),scale=1.6,position=self.node.position).autoRetain()
                elif self.blastType == "BdM":
                    node.handleMessage(bs.PowerupMessage(powerupType = 'curse'))
                elif self.blastType == "BdV":
                    node.handleMessage(bs.PowerupMessage(powerupType = 'health'))
                elif self.blastType == "magicBomb":          
                	bsUtils.PopupText("MAGIA!",color=(1.2,0.3,0),scale=1.6,position=self.node.position).autoRetain()
                elif self.blastType == "iceImpact":
                    bs.playSound(Bomb.getFactory().freezeSound, 10, position=t)
                    node.handleMessage(bs.FreezeMessage())
                elif self.blastType == "luckyBomb":
                	#node.handleMessage(bs.PowerupMessage(powerupType = 'palMostro'))
                    node.handleMessage(bs.PowerupMessage(powerupType = random.choice(['health','shield','speed','tripleBombs','iceBombs','impactBombs','iceImpact','deathOrb','tntBombs','us','extraLive','luckyBlock','luckyBlock','luckyBlock','luckyBlock','landMines','stickyBombs','power'])))
                elif self.blastType == "mostro":
                	node.handleMessage(bs.PowerupMessage(powerupType = 'palMostro'))
                elif self.blastType == "endBomb":
                	node.handleMessage(bs.ShouldShatterMessage())
                    #node.handleMessage(bs.DieMessage())
                elif self.blastType == "electric":
                	node.handleMessage(bs.ElectricMessage())
                elif self.blastType == "bugBomb":
                	#node.handleMessage(bs.PowerupMessage(powerupType = 'bugMessage'))
                	#node.run = 20
                	node.handleMessage(bs.BugMessage())
                elif self.blastType == "eggBomb":
                    bs.getActivity().mBotSet = bs.BotSet()
                    bs.getActivity().mBotSet.spawnBot(self._getRandomBotType(),pos=self.node.position,spawnTime = 0)
                elif self.blastType == "shockBomb":
                	node.handleMessage(bs.PowerupMessage(powerupType = 'shock'))
                    #ShockWave(position = self.node.position)
        else:
            bs.Actor.handleMessage(self, msg)
   

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

class Bomb(bs.Actor):
    """
    category: Game Flow Classes
    
    A bomb and its variants such as land-mines and tnt-boxes.
    """

    def __init__(self, position=(0,1,0), velocity=(0,0,0), bombType='normal',
                 blastRadius=2.0, sourcePlayer=None, owner=None):
        """
        Create a new Bomb.
        
        bombType can be 'ice','impact','landMine','normal','sticky', or 'tnt'.
        Note that for impact or landMine bombs you have to call arm()
        before they will go off.
        """
        bs.Actor.__init__(self)
        self.aim = None

        factory = self.getFactory()

        if not bombType in ('ice','impact','landMine','normal','sticky','tnt','espectralBomb','magicBomb','tntImpact','iceImpact','endBomb','powerupBomb','saltarina','upSticky','electric','luckyBomb','BdM','mostro','BdV','crazyBomb','fireBomb','party','bugBomb','menu','eggBomb','dirigida','iceDirigida','shockBomb'):
            raise Exception("invalid bomb type: " + bombType)
        self.bombType = bombType

        self._exploded = False

        if self.bombType == 'sticky' or self.bombType == 'upSticky': self._lastStickySoundTime = 0

        self.blastRadius = blastRadius
        if self.bombType == 'ice': self.blastRadius *= 1.2
        elif self.bombType == 'crazyBomb': self.blastRadius *= 0.7
        elif self.bombType == 'eggBomb': self.blastRadius *= 1.3
        elif self.bombType == 'impact': self.blastRadius *= 0.7
        elif self.bombType == 'landMine': self.blastRadius *= 0.7
        elif self.bombType == 'powerupBomb': self.blastRadius *= 0.8
        elif self.bombType == 'tntImpact': self.blastRadius *= 1.25
        elif self.bombType == 'tnt': self.blastRadius *= 1.45
        elif self.bombType == 'espectralBomb': self.blastRadius *= 0.8
        elif self.bombType == 'party': self.blastRadius *= 0
        elif self.bombType == 'fireBomb': self.blastRadius *= 1.2
        elif self.bombType == 'mostro': self.blastRadius *= 1
        elif self.bombType == 'BdM': self.blastRadius *= 1.1
        elif self.bombType == 'BdV': self.blastRadius *= 1.1
        elif self.bombType == 'magicBomb': self.blastRadius *= 0.75
        elif self.bombType == 'iceImpact': self.blastRadius *= 1.3
        elif self.bombType == 'shockBomb': self.blastRadius *= 1.2
        elif self.bombType == 'menu': self.blastRadius *= 1
        elif self.bombType == 'endBomb': self.blastRadius *= 0.9
        elif self.bombType == 'saltarina': self.blastRadius *= 1.5
        elif self.bombType == 'electric': self.blastRadius *= 1.3
        elif self.bombType == 'bugBomb': self.blastRadius *= 1
        elif self.bombType == 'luckyBomb': self.blastRadius *= 1.0
        elif self.bombType == 'dirigida': self.blastRadius *= 1.5
        elif self.bombType == 'iceDirigida': self.blastRadius *= 1.2

        self._explodeCallbacks = []
        
        # the player this came from
        self.sourcePlayer = sourcePlayer

        # by default our hit type/subtype is our own, but we pick up types of
        # whoever sets us off so we know what caused a chain reaction
        self.hitType = 'explosion'
        self.hitSubType = self.bombType

        # if no owner was provided, use an unconnected node ref
        if owner is None: owner = bs.Node(None)

        # the node this came from
        self.owner = owner

        # adding footing-materials to things can screw up jumping and flying
        # since players carrying those things
        # and thus touching footing objects will think they're on solid ground..
        # perhaps we don't wanna add this even in the tnt case?..
        if self.bombType == 'tnt':
            materials = (factory.bombMaterial,
                         bs.getSharedObject('footingMaterial'),
                         bs.getSharedObject('objectMaterial'))
        else:
            materials = (factory.bombMaterial,
                         bs.getSharedObject('objectMaterial'))
            
        if self.bombType == 'impact' or self.bombType == 'espectralBomb' or self.bombType == 'BdM' or self.bombType == 'magicBomb' or self.bombType == 'tntImpact' or self.bombType == 'iceImpact' or self.bombType == 'luckyBomb' or self.bombType == 'mostro' or self.bombType == 'BdV' or self.bombType == 'fireBomb' or self.bombType == 'bugBomb' or self.bombType == 'menu' or self.bombType == 'eggBomb' or self.bombType == 'dirigida' or self.bombType == 'shockBomb' or self.bombType == 'iceDirigida':
            materials = materials + (factory.impactBlastMaterial,)
        elif self.bombType == 'landMine' or self.bombType == 'powerupBomb':
            materials = materials + (factory.landMineNoExplodeMaterial,)

        if self.bombType == 'sticky':
            materials = materials + (factory.stickyMaterial,)
        if self.bombType == 'upSticky': 
            materials = materials + (factory.stickyMaterial,)
        else:
            materials = materials + (factory.normalSoundMaterial,)

        if self.bombType == 'landMine':
            self.node = bs.newNode('prop', delegate=self, attrs={
                'position':position,
                'velocity':velocity,
                'model':factory.landMineModel,
                'lightModel':factory.landMineModel,
                'body':'landMine',
                'shadowSize':0.44,
                'colorTexture':factory.landMineTex,
                'reflection':'powerup',
                'reflectionScale':[1.0],
                'materials':materials})
                
        elif self.bombType == 'powerupBomb':
            self.node = bs.newNode('prop', delegate=self, attrs={
                'position':position,
                'velocity':velocity,
                'model':factory.powerupBombModel,
                'lightModel':factory.powerupBombModelS,
                'body':'crate',
                'bodyScale':0.9,
                'shadowSize':0.5,
                'colorTexture':(random.choice([factory.cube1Tex,
                                                                        factory.cube2Tex,
                                                                        factory.cube3Tex,
                                                                        factory.cube4Tex,
                                                                        factory.cube5Tex,
                                                                        factory.cube6Tex,
                                                                        factory.cube7Tex,
                                                                        factory.cube8Tex,
                                                                        factory.cube9Tex])),
                'reflection':'powerup',
                'reflectionScale':[0.5],
                'materials':materials})
            #self._animateTimer = bs.Timer(1000,bs.WeakCall(self._addAnimate),repeat=True)
            #self.shield1 = bs.newNode('shield',owner=self.node,
                                     #attrs={'color':(random.random()*3,random.random()*3,random.random()*3),'radius':0.86})
            #self.node.connectAttr('position',self.shield1,'position')

        elif self.bombType == 'tnt':
            self.node = bs.newNode('prop', delegate=self, attrs={
                'position':position,
                'velocity':velocity,
                'model':factory.tntModel,
                'lightModel':factory.tntModel,
                'body':'crate',
                'shadowSize':0.5,
                'colorTexture':factory.tntTex,
                'reflection':'soft',
                'reflectionScale':[0.23],
                'materials':materials})
                
        elif self.bombType == 'espectralBomb':
            fuseTime = 900000
            self.node = bs.newNode('prop',
                                   delegate=self,
                                   attrs={'position':position,
                                          'velocity':velocity,
                                          'body':'sphere',                                         
                                          'materials':materials})
            self.armTimer = bs.Timer(200,bs.WeakCall(self.handleMessage,ArmMessage()))
            self.warnTimer = bs.Timer(fuseTime-1700,bs.WeakCall(self.handleMessage,WarnMessage()))

            self.shield1 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(2,2,2),'radius':0.7})
            self.node.connectAttr('position',self.shield1,'position')
            
            self.shield2 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(0,50,50),'radius':0.4})
            self.node.connectAttr('position',self.shield2,'position')
            
            self.shield3 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(30,30,30),'radius':0.6})
            self.node.connectAttr('position',self.shield3,'position')
            
            bs.animate(self.shield2,'radius',{0:0.1,100:0.5,600:0.1},True)
            
        elif self.bombType == 'party':
            fuseTime = 900000
            self.node = bs.newNode('prop',
                                   delegate=self,
                                   attrs={'position':position,
                                          'velocity':velocity,
                                          'body':'sphere',                                         
                                          'materials':materials})
            self.armTimer = bs.Timer(200,bs.WeakCall(self.handleMessage,ArmMessage()))
            self.warnTimer = bs.Timer(fuseTime-1700,bs.WeakCall(self.handleMessage,WarnMessage()))

            self.shield1 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(random.random()*6,random.random()*6,random.random()*6),'radius':0.7})
            self.node.connectAttr('position',self.shield1,'position')
            
            bs.animate(self.shield1,'radius',{0:0.5,250:1.0,500:0.5},True)
            
        elif self.bombType == 'fireBomb':
            fuseTime = 90000
            self.node = bs.newNode('prop',
                                   delegate=self,
                                   attrs={'position':position,
                                          'velocity':velocity,
                                          'body':'sphere',                                         
                                          'materials':materials})
            self.armTimer = bs.Timer(200,bs.WeakCall(self.handleMessage,ArmMessage()))
            self.warnTimer = bs.Timer(fuseTime-1700,bs.WeakCall(self.handleMessage,WarnMessage()))

            self.shield1 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(1*3,0.5*3,0),'radius':0.4})
            self.node.connectAttr('position',self.shield1,'position')
            self.shield2 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(1*3,0.5*3,0),'radius':0.5})
            self.node.connectAttr('position',self.shield2,'position')
            self.shield3 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(1*4,0.5*4,0),'radius':0.5})
            self.node.connectAttr('position',self.shield3,'position')
            self._trailFireTimer = bs.Timer(10,bs.WeakCall(self._addTrailFire),repeat=True)
            
        elif self.bombType == 'mostro':
            fuseTime = 900000
            self.node = bs.newNode('prop',
                                   delegate=self,
                                   attrs={'position':position,
                                          'velocity':velocity,
                                          'body':'sphere',                                         
                                          'materials':materials})
            self.armTimer = bs.Timer(200,bs.WeakCall(self.handleMessage,ArmMessage()))
            self.warnTimer = bs.Timer(fuseTime-1700,bs.WeakCall(self.handleMessage,WarnMessage()))

            self.shield1 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(5,0,0),'radius':0.7})
            self.node.connectAttr('position',self.shield1,'position')
            
            self.shield2 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(0,5,0),'radius':0.4})
            self.node.connectAttr('position',self.shield2,'position')
            
            self.shield3 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(0,0,5),'radius':0.6})
            self.node.connectAttr('position',self.shield3,'position')
            
            bs.animate(self.shield2,'radius',{0:0.1,300:1.5,400:0.1},True)

        elif self.bombType == 'BdM':
            fuseTime = 900000
            self.node = bs.newNode('prop',
                                   delegate=self,
                                   attrs={'position':position,
                                          'velocity':velocity,
                                          'body':'sphere',                                         
                                          'materials':materials})
            self.armTimer = bs.Timer(200,bs.WeakCall(self.handleMessage,ArmMessage()))
            self.warnTimer = bs.Timer(fuseTime-1700,bs.WeakCall(self.handleMessage,WarnMessage()))

            self.shield1 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(0,0,0),'radius':0.7})
            self.node.connectAttr('position',self.shield1,'position')
            
            self.shield2 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(20,0,0),'radius':0.4})
            self.node.connectAttr('position',self.shield2,'position')
            
            self.shield3 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(0,0,0),'radius':0.7})
            self.node.connectAttr('position',self.shield3,'position')
            
            self.shield4 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(0,0,0),'radius':0.7})
            self.node.connectAttr('position',self.shield4,'position')
            
            self.shield5 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(0,0,0),'radius':0.7})
            self.node.connectAttr('position',self.shield5,'position')
            
            self.shield6 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(0,0,0),'radius':0.7})
            self.node.connectAttr('position',self.shield6,'position')
            
            self.shield7 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(0,0,0),'radius':0.7})
            self.node.connectAttr('position',self.shield7,'position')
            
            self.shield8 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(0,0,0),'radius':0.7})
            self.node.connectAttr('position',self.shield8,'position')
            
            self.shield9 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(0,0,0),'radius':0.7})
            self.node.connectAttr('position',self.shield9,'position')
            
            self.shield10 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(0,0,0),'radius':0.7})
            self.node.connectAttr('position',self.shield10,'position')
            
            self.shield11 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(0,0,0),'radius':0.7})
            self.node.connectAttr('position',self.shield11,'position')
            
            self.shield12 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(0,0,0),'radius':0.7})
            self.node.connectAttr('position',self.shield12,'position')
            
            self.shield13 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(0,0,0),'radius':0.7})
            self.node.connectAttr('position',self.shield13,'position')
            
            self.shield14 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(0.5,0,0),'radius':0.7})
            self.node.connectAttr('position',self.shield14,'position')
            
            bs.animate(self.shield2,'radius',{0:0.1,100:0.5,600:0.1},True)        
            
        elif self.bombType == 'BdV':
            fuseTime = 900000
            self.node = bs.newNode('prop',
                                   delegate=self,
                                   attrs={'position':position,
                                          'velocity':velocity,
                                          'body':'sphere',                                         
                                          'materials':materials})
            self.armTimer = bs.Timer(200,bs.WeakCall(self.handleMessage,ArmMessage()))
            self.warnTimer = bs.Timer(fuseTime-1700,bs.WeakCall(self.handleMessage,WarnMessage()))

            self.shield1 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(1,1,1),'radius':0.7})
            self.node.connectAttr('position',self.shield1,'position')
            
            self.shield2 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(20,0,0),'radius':0.4})
            self.node.connectAttr('position',self.shield2,'position')
            
            self.shield3 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(1,1,1),'radius':0.7})
            self.node.connectAttr('position',self.shield3,'position')
            
            self.shield4 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(2,2,2),'radius':0.7})
            self.node.connectAttr('position',self.shield4,'position')
            
            bs.animate(self.shield2,'radius',{0:0.1,100:0.5,600:0.1},True)        
            
        elif self.bombType == 'electric':
            fuseTime = 3000
            self.node = bs.newNode('prop',
                                   delegate=self,
                                   attrs={'position':position,
                                          'velocity':velocity,
                                          'body':'sphere',                                         
                                          'materials':materials})

            self.shield1 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(10,10,10),'radius':0.7})
            self.node.connectAttr('position',self.shield1,'position')
            
            self.shield2 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(0,0,20),'radius':0.5})
            self.node.connectAttr('position',self.shield2,'position')
            
            self.shield3 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(0,10,10),'radius':0.5})
            self.node.connectAttr('position',self.shield3,'position')
            
            self.shield4 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(30,0,0),'radius':0.2})
            self.node.connectAttr('position',self.shield4,'position')
            
            bs.animate(self.shield2,'radius',{0:0.1,10:0.7,500:0.3},True) 
            bs.animate(self.shield3,'radius',{0:0.1,10:1.0,700:0.5},True) 
            self._trailFireTimer = bs.Timer(0,bs.WeakCall(self._Text),repeat=False)
            
        elif self.bombType == 'bugBomb':
            fuseTime = 20000
            self.node = bs.newNode('prop',
                                   delegate=self,
                                   attrs={'position':position,
                                          'velocity':velocity,
                                          'body':'sphere',                                         
                                          'materials':materials})

            self.shield1 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(1,0,0),'radius':0.7})
            self.node.connectAttr('position',self.shield1,'position')
            
            self.shield2 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(0,0,2),'radius':0.5})
            self.node.connectAttr('position',self.shield2,'position')
            
            self.shield3 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(0,1,1),'radius':0.5})
            self.node.connectAttr('position',self.shield3,'position')
            
            self.shield4 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(3,3,0),'radius':0.2})
            self.node.connectAttr('position',self.shield4,'position')
            
            bs.animate(self.shield2,'radius',{0:0.1,10:1.5,500:0.3},True) 
            bs.animate(self.shield3,'radius',{0:0.1,10:1.0,700:0.5},True) 
            
        elif self.bombType == 'magicBomb':
            fuseTime = 900000
            self.node = bs.newNode('prop',
                                   delegate=self,
                                   attrs={'position':position,
                                          'velocity':velocity,
                                          'body':'sphere',                                         
                                          'materials':materials})
            self.armTimer = bs.Timer(200,bs.WeakCall(self.handleMessage,ArmMessage()))
            self.warnTimer = bs.Timer(fuseTime-1700,bs.WeakCall(self.handleMessage,WarnMessage()))

            self.shield1 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(0,0,20),'radius':0.7})
            self.node.connectAttr('position',self.shield1,'position')
            
            self.shield2 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(20,20,20),'radius':0.4})
            self.node.connectAttr('position',self.shield2,'position')
            
            self.shield3 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(20,0,0),'radius':0.5})
            self.node.connectAttr('position',self.shield3,'position')
            
            bs.animate(self.shield2,'radius',{0:0.1,100:0.2,600:0.1},True)                                          
            bs.animate(self.shield1,'radius',{0:0.4,100:0.7,300:0.4},True)
            
        elif self.bombType == 'iceImpact':
            fuseTime = 900000
            self.node = bs.newNode('prop',
                                   delegate=self,
                                   attrs={'position':position,
                                          'velocity':velocity,
                                          'body':'sphere',                                         
                                          'materials':materials})
            self.armTimer = bs.Timer(200,bs.WeakCall(self.handleMessage,ArmMessage()))
            self.warnTimer = bs.Timer(fuseTime-1700,bs.WeakCall(self.handleMessage,WarnMessage()))

            self.shield1 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(0,0,20),'radius':0.7})
            self.node.connectAttr('position',self.shield1,'position')
            
            self.shield2 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(20,20,20),'radius':0.4})
            self.node.connectAttr('position',self.shield2,'position')
            
            self.shield3 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(0,10,10),'radius':0.6})
            self.node.connectAttr('position',self.shield3,'position')
            
            bs.animate(self.shield2,'radius',{0:0.1,100:0.2,600:0.1},True)                                          
            bs.animate(self.shield1,'radius',{0:0.4,100:0.7,300:0.4},True)
            
        elif self.bombType == 'shockBomb':
            fuseTime = 900000
            self.node = bs.newNode('prop',
                                   delegate=self,
                                   attrs={'position':position,
                                          'velocity':velocity,
                                          'body':'sphere',                                         
                                          'materials':materials})
            self.armTimer = bs.Timer(200,bs.WeakCall(self.handleMessage,ArmMessage()))
            self.warnTimer = bs.Timer(fuseTime-1700,bs.WeakCall(self.handleMessage,WarnMessage()))

            self.shield1 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(3,0,5),'radius':0.7})
            self.node.connectAttr('position',self.shield1,'position')
            
            self.shield2 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(5,5,2),'radius':0.4})
            self.node.connectAttr('position',self.shield2,'position')
            
            self.shield3 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(0,0,5),'radius':0.6})
            self.node.connectAttr('position',self.shield3,'position')
            
            bs.animate(self.shield2,'radius',{0:0.3,100:0.5,600:0.3},True)                                          
            bs.animate(self.shield1,'radius',{0:0.4,100:0.7,300:0.4},True)
            
        elif self.bombType == 'menu':
            fuseTime = 900000
            self.node = bs.newNode('prop',
                                   delegate=self,
                                   attrs={'position':position,
                                          'velocity':velocity,
                                          'body':'sphere',                                         
                                          'materials':materials})
            self.armTimer = bs.Timer(200,bs.WeakCall(self.handleMessage,ArmMessage()))
            self.warnTimer = bs.Timer(fuseTime-1700,bs.WeakCall(self.handleMessage,WarnMessage()))

            self.shield1 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(random.random()*10,random.random()*10,random.random()*10),'radius':0.7})
            self.node.connectAttr('position',self.shield1,'position')
            
            self.shield2 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(random.random()*10,random.random()*10,random.random()*10),'radius':0.4})
            self.node.connectAttr('position',self.shield2,'position')
            
            self.shield3 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(random.random()*10,random.random()*10,random.random()*10),'radius':0.4})
            self.node.connectAttr('position',self.shield3,'position')
            
            bs.animate(self.shield2,'radius',{0:0.1,100:0.2,600:0.1},True)                                          
            bs.animate(self.shield1,'radius',{0:0.1,100:0.2,300:0.1},True)
            #self._trailSparkTimer = bs.Timer(10,bs.WeakCall(self._addTrailSpark),repeat=True)
            
        elif self.bombType == 'luckyBomb':
            fuseTime = 900000
            self.node = bs.newNode('prop',
                                   delegate=self,
                                   attrs={'position':position,
                                          'velocity':velocity,
                                          'body':'sphere',                                         
                                          'materials':materials})
            self.armTimer = bs.Timer(200,bs.WeakCall(self.handleMessage,ArmMessage()))
            self.warnTimer = bs.Timer(fuseTime-1700,bs.WeakCall(self.handleMessage,WarnMessage()))

            self.shield1 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(0,0,1),'radius':1.0})
            self.node.connectAttr('position',self.shield1,'position')
            
            self.shield2 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(0,1,0),'radius':0.9})
            self.node.connectAttr('position',self.shield2,'position')
            
            self.shield3 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(1,0,0),'radius':0.8})
            self.node.connectAttr('position',self.shield3,'position')
            
            self.shield4 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(0,1,1),'radius':0.7})
            self.node.connectAttr('position',self.shield4,'position')
            
            self.shield5 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(1,0,1),'radius':0.6})
            self.node.connectAttr('position',self.shield5,'position')
            
            self.shield6 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(1,1,0),'radius':0.5})
            self.node.connectAttr('position',self.shield6,'position')
            
            self.shield7 = bs.newNode('shield',owner=self.node,
                                     attrs={'color':(1,1,1),'radius':0.2})
            self.node.connectAttr('position',self.shield7,'position')
            
            bs.animate(self.shield7,'radius',{0:0.1,100:0.2,600:0.1},True)                                          
            
        elif self.bombType == 'saltarina':
            fuseTime = 5000
            self.node = bs.newNode('prop',
                                   delegate=self,
                                   attrs={'position':position,
                                          'velocity':velocity,
                                          'model':factory.bombModel,
                                          'lightModel':factory.bombModel,
                                          'body':'sphere',
                                          'shadowSize':0.5,
                                          'colorTexture':factory.saltarinaTex,
                                          'reflection':'powerup',
                                          'reflectionScale':[0.5],
                                          'materials':materials})
            self._animateTimer = bs.Timer(1000,bs.WeakCall(self._addAnimate),repeat=True)
            self._trailFireTimer = bs.Timer(0,bs.WeakCall(self._Text2),repeat=False)
            
        elif self.bombType == 'impact':
            fuseTime = 20000
            self.node = bs.newNode('prop', delegate=self, attrs={
                'position':position,
                'velocity':velocity,
                'body':'sphere',
                'model':factory.impactBombModel,
                'shadowSize':0.3,
                'colorTexture':factory.impactTex,
                'reflection':'powerup',
                'reflectionScale':[1.5],
                'materials':materials})
            self.armTimer = bs.Timer(200, bs.WeakCall(self.handleMessage,
                                                      ArmMessage()))
            self.warnTimer = bs.Timer(fuseTime-1700,
                                      bs.WeakCall(self.handleMessage,
                                                  WarnMessage()))
                                                  
        elif self.bombType == 'eggBomb':
            fuseTime = 20000
            self.node = bs.newNode('prop', delegate=self, attrs={
                'position':position,
                'velocity':velocity,
                'body':'sphere',
                'model':factory.eggBombModel,
                'shadowSize':0.3,
                'colorTexture':(random.choice([factory.eggTex,
                                                                        factory.egg2Tex,
                                                                        factory.egg3Tex,])),
                'reflection':'powerup',
                'reflectionScale':[1.5],
                'materials':materials})
            self.armTimer = bs.Timer(200, bs.WeakCall(self.handleMessage,
                                                      ArmMessage()))
            self.warnTimer = bs.Timer(fuseTime-1700,
                                      bs.WeakCall(self.handleMessage,
                                                  WarnMessage()))
                                                  
        elif self.bombType == 'tntImpact':
            fuseTime = 25000
            self.node = bs.newNode('prop',
                                   delegate=self,
                                   attrs={'position':position,
                                          'velocity':velocity,
                                          'body':'sphere',
                                          'model':factory.impactBombModel,
                                          'shadowSize':0.3,
                                          'colorTexture':factory.tntTex,
                                          'reflection':'powerup',
                                          'reflectionScale':[1.5],
                                          'materials':materials})
            self.armTimer = bs.Timer(200,bs.WeakCall(self.handleMessage, ArmMessage()))
            self.warnTimer = bs.Timer(fuseTime-1700,bs.WeakCall(self.handleMessage, WarnMessage()))

        else:
            fuseTime = 3000
            if self.bombType == 'sticky':
                sticky = True
                model = factory.stickyBombModel
                rType = 'sharper'
                rScale = 1.8
            elif self.bombType == 'dirigida':
            	fuseTime = 10000
                sticky = True
                model = factory.stickyBombModel
                rType = 'sharper'
                rScale = 0.0
            elif self.bombType == 'iceDirigida':
            	fuseTime = 10000
                sticky = True
                model = factory.iceDirigidaModel
                bodyScale = 1.0
                density = 999999999
                gravityScale = 200
                rType = 'sharper'
                rScale = 0.0
            elif self.bombType == 'crazyBomb':
            	fuseTime = 5000
                sticky = True
                model = factory.powerupBombModel
                rType = 'sharper'
                rScale = 0.0
                self._trailFireTimer = bs.Timer(10,bs.WeakCall(self._addTrailFire),repeat=True)
            elif self.bombType == 'upSticky':
            	fuseTime = 10000
                sticky = True
                model = factory.stickyBombModel
                rType = 'sharper'
                rScale = 0.0
                self._upTimer = bs.Timer(2000,bs.WeakCall(self._addUp),repeat=False)
            else:
                sticky = False
                model = factory.bombModel
                rType = 'sharper'
                rScale = 1.8
            if self.bombType == 'ice': tex = factory.iceTex
            elif self.bombType == 'crazyBomb': tex = factory.crazyBombTex
            elif self.bombType == 'sticky': tex = factory.stickyTex
            elif self.bombType == 'upSticky': tex = factory.stickyTex
            elif self.bombType == 'endBomb': tex = factory.endBombTex
            elif self.bombType == 'dirigida': tex = factory.dirigidaTex
            elif self.bombType == 'iceDirigida': tex = factory.iceDirigidaTex
            else: tex = factory.regularTex
            self.node = bs.newNode('bomb', delegate=self, attrs={
                'position':position,
                'velocity':velocity,
                'model':model,
                'shadowSize':0.3,
                'colorTexture':tex,
                'sticky':sticky,
                'owner':owner,
                'reflection':rType,
                'reflectionScale':[rScale],
                'materials':materials})

            sound = bs.newNode('sound', owner=self.node, attrs={
                'sound':factory.fuseSound,
                'volume':0.25})
            self.node.connectAttr('position', sound, 'position')
            bsUtils.animate(self.node, 'fuseLength', {0:1.0, fuseTime:0.0})

        # light the fuse!!!
        if self.bombType not in ('landMine','tnt','powerupBomb','dirigida','iceDirigida'):
            bs.gameTimer(fuseTime,
                         bs.WeakCall(self.handleMessage, ExplodeMessage()))
        
        bsUtils.animate(self.node,"modelScale",{0:0, 200:1.3, 260:1})

    def getSourcePlayer(self):
        """
        Returns a bs.Player representing the source of this bomb.
        """
        if self.sourcePlayer is None: return bs.Player(None) # empty player ref
        return self.sourcePlayer
        
    @classmethod
    def getFactory(cls):
        """
        Returns a shared bs.BombFactory object, creating it if necessary.
        """
        activity = bs.getActivity()
        try: return activity._sharedBombFactory
        except Exception:
            f = activity._sharedBombFactory = BombFactory()
            return f

    def onFinalize(self):
        bs.Actor.onFinalize(self)
        # release callbacks/refs so we don't wind up with dependency loops..
        self._explodeCallbacks = []
        
    def _handleDie(self,m):
        self.node.delete()
        
    def _handleOOB(self, msg):
        self.handleMessage(bs.DieMessage())

    def _handleImpact(self, m):
        node,body = bs.getCollisionInfo("opposingNode","opposingBody")
        # if we're an impact bomb and we came from this node, don't explode...
        # alternately if we're hitting another impact-bomb from the same source,
        # don't explode...
        try: nodeDelegate = node.getDelegate()
        except Exception: nodeDelegate = None
        if node is not None and node.exists():
            if (self.bombType == 'impact' and
                (node is self.owner
                 or (isinstance(nodeDelegate, Bomb)
                     and nodeDelegate.bombType == 'impact'
                     and nodeDelegate.owner is self.owner))): return
            if (self.bombType == 'espectralBomb' and
                (node is self.owner or (isinstance(nodeDelegate,Bomb) and nodeDelegate.bombType == 'espectralBomb' and nodeDelegate.owner is self.owner))): return                
            if (self.bombType == 'eggBomb' and
                (node is self.owner or (isinstance(nodeDelegate,Bomb) and nodeDelegate.bombType == 'eggBomb' and nodeDelegate.owner is self.owner))): return                
            if (self.bombType == 'fireBomb' and
                (node is self.owner or (isinstance(nodeDelegate,Bomb) and nodeDelegate.bombType == 'fireBomb' and nodeDelegate.owner is self.owner))): return                
            if (self.bombType == 'mostro' and
                (node is self.owner or (isinstance(nodeDelegate,Bomb) and nodeDelegate.bombType == 'mostro' and nodeDelegate.owner is self.owner))): return                
            if (self.bombType == 'BdM' and
                (node is self.owner or (isinstance(nodeDelegate,Bomb) and nodeDelegate.bombType == 'BdM' and nodeDelegate.owner is self.owner))): return                
            if (self.bombType == 'BdV' and
                (node is self.owner or (isinstance(nodeDelegate,Bomb) and nodeDelegate.bombType == 'BdV' and nodeDelegate.owner is self.owner))): return                
            if (self.bombType == 'magicBomb' and
                (node is self.owner or (isinstance(nodeDelegate,Bomb) and nodeDelegate.bombType == 'magicBomb' and nodeDelegate.owner is self.owner))): return                
            if (self.bombType == 'iceImpact' and
                (node is self.owner or (isinstance(nodeDelegate,Bomb) and nodeDelegate.bombType == 'iceImpact' and nodeDelegate.owner is self.owner))): return                
            if (self.bombType == 'shockBomb' and
                (node is self.owner or (isinstance(nodeDelegate,Bomb) and nodeDelegate.bombType == 'shockBomb' and nodeDelegate.owner is self.owner))): return                
            if (self.bombType == 'menu' and
                (node is self.owner or (isinstance(nodeDelegate,Bomb) and nodeDelegate.bombType == 'menu' and nodeDelegate.owner is self.owner))): return                
            if (self.bombType == 'luckyBomb' and
                (node is self.owner or (isinstance(nodeDelegate,Bomb) and nodeDelegate.bombType == 'luckyBomb' and nodeDelegate.owner is self.owner))): return                
            if (self.bombType == 'bugBomb' and
                (node is self.owner or (isinstance(nodeDelegate,Bomb) and nodeDelegate.bombType == 'bugBomb' and nodeDelegate.owner is self.owner))): return                
            if (self.bombType == 'tntImpact' and
                (node is self.owner or (isinstance(nodeDelegate,Bomb) and nodeDelegate.bombType == 'tntImpact' and nodeDelegate.owner is self.owner))): return
            else:
                self.handleMessage(ExplodeMessage())
              
                
    def _handleDirigida(self,msg):
        node = bs.getCollisionInfo("opposingNode")
        if self.node.exists():
            if node is not self.owner and bs.getSharedObject('playerMaterial') in node.materials:
                self.node.sticky = True
                def on():
                    self.node.extraAcceleration = (0,80,0)
                    #node.holdNode = self.node
                    if self.aim is not None:
                        self.aim.off()
                bs.gameTimer(2,on)
                
    def _handleIceDirigida(self,msg):
        node = bs.getCollisionInfo("opposingNode")
        if self.node.exists():
            if node is not self.owner and bs.getSharedObject('playerMaterial') in node.materials:
                self.node.sticky = True
                def on():
                	#self.node.invincible = True
                	#bs.Blast(position=self.node.position, blastRadius=0.5, blastType='ice').autoRetain()
                    self.node.extraAcceleration = (0,-100,0)
                    if self.aim is not None:
                        self.aim.off()
                bs.gameTimer(2,on)

    def _handleDropped(self,m):
        if self.bombType == 'landMine':
            self.armTimer = \
                bs.Timer(1250, bs.WeakCall(self.handleMessage, ArmMessage()))
        elif self.bombType == 'powerupBomb':
            self.armTimer = \
                bs.Timer(750, bs.WeakCall(self.handleMessage, ArmMessage()))
        elif self.bombType == 'dirigida':
            self.armTimer = \
                bs.Timer(50, bs.WeakCall(self.handleMessage, ArmMessage()))
        elif self.bombType == 'iceDirigida':
            self.armTimer = \
                bs.Timer(50, bs.WeakCall(self.handleMessage, ArmMessage()))

        # once we've thrown a sticky bomb we can stick to it..
        elif self.bombType == 'sticky':
            def _safeSetAttr(node,attr,value):
                if node.exists(): setattr(node,attr,value)
            bs.gameTimer(
                250, lambda: _safeSetAttr(self.node, 'stickToOwner', True))

    def _handleSplat(self,m):
        node = bs.getCollisionInfo("opposingNode")
        if (node is not self.owner
                and bs.getGameTime() - self._lastStickySoundTime > 1000):
            self._lastStickySoundTime = bs.getGameTime()
            bs.playSound(self.getFactory().stickyImpactSound, 2.0,
                         position=self.node.position)

    def addExplodeCallback(self,call):
        """
        Add a call to be run when the bomb has exploded.
        The bomb and the new blast object are passed as arguments.
        """
        self._explodeCallbacks.append(call)
        
    def explode(self):
        """
        Blows up the bomb if it has not yet done so.
        """
        if self._exploded: return
        self._exploded = True
        activity = self.getActivity()
        if activity is not None and self.node.exists():
            if self.bombType == 'saltarina':
                #blast = Blast(position=self.node.position,velocity=self.node.velocity,blastRadius=self.blastRadius,blastType=self.bombType,sourcePlayer=self.sourcePlayer,hitType=self.hitType,hitSubType=self.hitSubType).autoRetain()
                for c in self._explodeCallbacks: c(self,blast)
                t = self.node.position
                self.a = blast = Blast(position=(t[0],t[1],t[2]),velocity=self.node.velocity,blastRadius=self.blastRadius,blastType=self.bombType,sourcePlayer=self.sourcePlayer,hitType=self.hitType,hitSubType=self.hitSubType).autoRetain()
                self.b = blast = Blast(position=(t[0],t[1],t[2]+0.5),velocity=self.node.velocity,blastRadius=self.blastRadius,blastType=self.bombType,sourcePlayer=self.sourcePlayer,hitType=self.hitType,hitSubType=self.hitSubType).autoRetain()
                self.c = blast = Blast(position=(t[0],t[1],t[2]-0.5),velocity=self.node.velocity,blastRadius=self.blastRadius,blastType=self.bombType,sourcePlayer=self.sourcePlayer,hitType=self.hitType,hitSubType=self.hitSubType).autoRetain()
                self.d = blast = Blast(position=(t[0]+0.5,t[1],t[2]),velocity=self.node.velocity,blastRadius=self.blastRadius,blastType=self.bombType,sourcePlayer=self.sourcePlayer,hitType=self.hitType,hitSubType=self.hitSubType).autoRetain()
                self.ac = blast = Blast(position=(t[0]-0.5,t[1],t[2]+0.5),velocity=self.node.velocity,blastRadius=self.blastRadius,blastType=self.bombType,sourcePlayer=self.sourcePlayer,hitType=self.hitType,hitSubType=self.hitSubType).autoRetain()
                self.ad = blast = Blast(position=(t[0]-0.5,t[1],t[2]-0.5),velocity=self.node.velocity,blastRadius=self.blastRadius,blastType=self.bombType,sourcePlayer=self.sourcePlayer,hitType=self.hitType,hitSubType=self.hitSubType).autoRetain()
                self.ab = blast = Blast(position=(t[0]+0.5,t[1],t[2]+0.5),velocity=self.node.velocity,blastRadius=self.blastRadius,blastType=self.bombType,sourcePlayer=self.sourcePlayer,hitType=self.hitType,hitSubType=self.hitSubType).autoRetain()
                self.bc = blast = Blast(position=(t[0]-0.5,t[1],t[2]+0.5),velocity=self.node.velocity,blastRadius=self.blastRadius,blastType=self.bombType,sourcePlayer=self.sourcePlayer,hitType=self.hitType,hitSubType=self.hitSubType).autoRetain()
                self.bd = blast = Blast(position=(t[0]+0.5,t[1],t[2]-0.5),velocity=self.node.velocity,blastRadius=self.blastRadius,blastType=self.bombType,sourcePlayer=self.sourcePlayer,hitType=self.hitType,hitSubType=self.hitSubType).autoRetain()
            else:
                blast = Blast(position=self.node.position,velocity=self.node.velocity,blastRadius=self.blastRadius,blastType=self.bombType,sourcePlayer=self.sourcePlayer,hitType=self.hitType,hitSubType=self.hitSubType).autoRetain()
            
            if self.bombType == 'crazyBomb':
                    def slowMo():
                        bs.getSharedObject('globals').tint = (0.6,0.1,0.1)
                        bs.getSharedObject('globals').ambientColor = (1,0.1,0.1)
                        bs.Bomb(position=(self.node.position[0],self.node.position[1]+3,self.node.position[2]),blastRadius=15.0,bombType='endBomb').autoRetain()
                    slowMo()

                    def slowMo1():
                        bs.getSharedObject('globals').tint = (1.15,1.15,1.0)
                        bs.getSharedObject('globals').ambientColor = (1,1,1)
                    slowMo1()
                    bs.playSound(bs.getSound("orchestraHitBig2"))
                    bs.gameTimer(100,bs.Call(slowMo))
                    bs.gameTimer(7000,bs.Call(slowMo1))
        		
        bs.statAdd('Bomb Explosions')
        # we blew up so we need to go away
        bs.gameTimer(1, bs.WeakCall(self.handleMessage, bs.DieMessage()))

    def _handleWarn(self, m):
        if self.textureSequence.exists():
            self.textureSequence.rate = 30
            bs.playSound(self.getFactory().warnSound, 0.5,
                         position=self.node.position)

    def _addMaterial(self, material):
        if not self.node.exists(): return
        materials = self.node.materials
        if not material in materials:
            self.node.materials = materials + (material,)
        
    def _addTrailSpark(self):
        if self.node.exists():
            bs.emitBGDynamics(position=self.node.position,velocity=(0,1,0),count=5,spread=0.05,scale=0.6,chunkType='spark')
        else: 
            self._trailTimer = None
            
    def _addTrailFire(self):
        if self.node.exists():
            bs.emitBGDynamics(position=self.node.position,velocity=(0,1,0),count=30,spread=0.05,scale=2,chunkType='sweat')
        else: 
            self._trailFireTimer = None
            
    def _addImpulse(self):
        if self.node.exists():
            self.node.extraAcceleration = (0,45,0)
        else: 
            self._impulseTimer = None
            
    def _addDesImpulse(self):
        if self.node.exists():
            self.node.extraAcceleration = (0,-40,0)
        else: 
            self._desImpulseTimer = None
            
    def _addUp(self):
        if self.node.exists():
            self.node.extraAcceleration = (0,75,0)
        else: 
            self._upTimer = None
            
    def _addAtraction(self):
        if self.node.exists():
        	self.aim = AutoAim(self.node,self.owner)
            #self.node.extraAcceleration = (0,75,0)
        else: 
            self._atractionTimer = None
            
    def _addDown(self):
        if self.node.exists():
            self.node.extraAcceleration = (0,-30,0)
        else: 
            self._downTimer = None
            
    def _addAnimate(self):
        if self.node.exists():
            bs.gameTimer(250,bs.WeakCall(self._addImpulse))
            bs.gameTimer(500,bs.WeakCall(self._addDesImpulse))
            bs.gameTimer(750,bs.WeakCall(self._addImpulse))
            bs.gameTimer(1000,bs.WeakCall(self._addDesImpulse))
            bs.gameTimer(1250,bs.WeakCall(self._addImpulse))
            bs.gameTimer(1500,bs.WeakCall(self._addDesImpulse))
        else: 
            self._animateTimer = None
                                                
    def _5(self):
        if self.node.exists():
            bsUtils.PopupText("5",color=(1,1,1),scale=1.4,position=self.node.position).autoRetain()
        else: 
            self._5 = None
                        
    def _4(self):
        if self.node.exists():
            bsUtils.PopupText("4",color=(1,1,1),scale=1.4,position=self.node.position).autoRetain()
        else: 
            self._4 = None
                        
    def _3(self):
        if self.node.exists():
            bsUtils.PopupText("3",color=(1,1,1),scale=1.4,position=self.node.position).autoRetain()
        else: 
            self._3 = None
                        
    def _2(self):
        if self.node.exists():
            bsUtils.PopupText("2",color=(1,1,1),scale=1.4,position=self.node.position).autoRetain()
        else: 
            self._2 = None
                        
    def _1(self):
        if self.node.exists():
            bsUtils.PopupText("1",color=(1,1,1),scale=1.4,position=self.node.position).autoRetain()
        else: 
            self._1 = None
                                                
    def _0(self):
        if self.node.exists():
            bsUtils.PopupText("Boom!",color=(1*3,0,0),scale=1.4,position=self.node.position).autoRetain()
        else: 
            self._0 = None
                                                
    def _Text(self):
        if self.node.exists():
            bs.gameTimer(0,bs.WeakCall(self._3))
            bs.gameTimer(1000,bs.WeakCall(self._2))
            bs.gameTimer(2000,bs.WeakCall(self._1))
            bs.gameTimer(3000,bs.WeakCall(self._0))
        else: 
            self._Text = None
                                                            
    def _Text2(self):
        if self.node.exists():
            bs.gameTimer(0,bs.WeakCall(self._5))
            bs.gameTimer(1000,bs.WeakCall(self._4))
            bs.gameTimer(2000,bs.WeakCall(self._3))
            bs.gameTimer(3000,bs.WeakCall(self._2))
            bs.gameTimer(4000,bs.WeakCall(self._1))
        else: 
            self._Text2 = None
        
    def arm(self):
        """
        Arms land-mines and impact-bombs so
        that they will explode on impact.
        """
        if not self.node.exists(): return
        factory = self.getFactory()
        if self.bombType == 'landMine':
            self.textureSequence = \
                bs.newNode('textureSequence', owner=self.node, attrs={
                    'rate':30,
                    'inputTextures':(factory.landMineLitTex,
                                     factory.landMineTex)})
            bs.gameTimer(500,self.textureSequence.delete)
            # we now make it explodable.
            bs.gameTimer(250,bs.WeakCall(self._addMaterial,
                                         factory.landMineBlastMaterial))
        elif self.bombType == 'impact':
            self.textureSequence = \
                bs.newNode('textureSequence', owner=self.node, attrs={
                    'rate':100,
                    'inputTextures':(factory.impactLitTex,
                                     factory.impactTex,
                                     factory.impactTex)})
            bs.gameTimer(250, bs.WeakCall(self._addMaterial,
                                          factory.landMineBlastMaterial))
        elif self.bombType == 'powerupBomb':
            bs.gameTimer(10, bs.WeakCall(self._addMaterial,
                                          factory.landMineBlastMaterial))
        elif self.bombType == 'dirigida':
            bs.playSound(bs.getSound('activateBeep'),position = self.node.position)
            self.aim = AutoAim(self.node,self.owner)
        elif self.bombType == 'iceDirigida':
            bs.playSound(bs.getSound('activateBeep'),position = self.node.position)
            self.aim = AutoAim2(self.node,self.owner)
        else:
            raise Exception('arm() should only be called '
                            'on land-mines or impact bombs')
        self.textureSequence.connectAttr('outputTexture',
                                         self.node, 'colorTexture')
        bs.playSound(factory.activateSound, 0.5, position=self.node.position)
        
    def _handleHit(self, msg):
        isPunch = (msg.srcNode.exists() and msg.srcNode.getNodeType() == 'spaz')

        # normal bombs are triggered by non-punch impacts..
        # impact-bombs by all impacts
        if (not self._exploded and not isPunch
            or self.bombType in ['impact', 'landMine','powerupBomb']):
            # also lets change the owner of the bomb to whoever is setting
            # us off.. (this way points for big chain reactions go to the
            # person causing them)
            if msg.sourcePlayer not in [None]:
                self.sourcePlayer = msg.sourcePlayer

                # also inherit the hit type (if a landmine sets off by a bomb,
                # the credit should go to the mine)
                # the exception is TNT.  TNT always gets credit.
                if self.bombType != 'tnt':
                    self.hitType = msg.hitType
                    self.hitSubType = msg.hitSubType

            bs.gameTimer(100+int(random.random()*100),
                         bs.WeakCall(self.handleMessage, ExplodeMessage()))
        self.node.handleMessage(
            "impulse", msg.pos[0], msg.pos[1], msg.pos[2],
            msg.velocity[0], msg.velocity[1], msg.velocity[2],
            msg.magnitude, msg.velocityMagnitude, msg.radius, 0,
            msg.velocity[0], msg.velocity[1], msg.velocity[2])

        if msg.srcNode.exists():
            pass
        
    def handleMessage(self, msg):
        if isinstance(msg, ExplodeMessage): self.explode()
        elif isinstance(msg, ImpactMessage): #self._handleImpact(m, typeOfBomb=self.bombType) #self._handleImpact(msg)
            if not self.bombType in ['dirigida','iceDirigida']:
                self._handleImpact(msg)
            elif self.bombType == 'dirigida':
                self._handleDirigida(msg)
            elif self.bombType == 'iceDirigida':
                self._handleIceDirigida(msg)
        elif isinstance(msg, bs.PickedUpMessage):
            # change our source to whoever just picked us up *only* if its None
            # this way we can get points for killing bots with their own bombs
            # hmm would there be a downside to this?...
            if self.sourcePlayer is not None:
                self.sourcePlayer = msg.node.sourcePlayer
        elif isinstance(msg, SplatMessage): self._handleSplat(msg)
        elif isinstance(msg, bs.DroppedMessage): self._handleDropped(msg)
        elif isinstance(msg, bs.HitMessage): self._handleHit(msg)
        elif isinstance(msg, bs.DieMessage): self._handleDie(msg)
        elif isinstance(msg, bs.OutOfBoundsMessage): self._handleOOB(msg)
        elif isinstance(msg, ArmMessage): self.arm()
        elif isinstance(msg, WarnMessage): self._handleWarn(msg)
        else: bs.Actor.handleMessage(self, msg)

class TNTSpawner(object):
    """
    category: Game Flow Classes

    Regenerates TNT at a given point in space every now and then.
    """
    def __init__(self,position,respawnTime=30000):
        """
        Instantiate with a given position and respawnTime (in milliseconds).
        """
        self._position = position
        self._tnt = None
        self._update()
        self._updateTimer = bs.Timer(1000,bs.WeakCall(self._update),repeat=True)
        self._respawnTime = int(random.uniform(0.8,1.2)*respawnTime)
        self._waitTime = 0
        
    def _update(self):
        tntAlive = self._tnt is not None and self._tnt.node.exists()
        if not tntAlive:
            # respawn if its been long enough.. otherwise just increment our
            # how-long-since-we-died value
            if self._tnt is None or self._waitTime >= self._respawnTime:
                self._tnt = Bomb(position=self._position,bombType='tnt')
                self._waitTime = 0
            else: self._waitTime += 1000
            
class AutoAim(object):
    def __init__(self,whoControl,owner,aliveOnly = True):
        
        self.whoControl = whoControl
        self.owner = owner
        self.aliveOnly = aliveOnly
        self.target = None
        
        self.aimZoneSpaz = bs.Material()
        self.aimZoneSpaz.addActions(conditions=(('theyHaveMaterial', bs.getSharedObject('playerMaterial'))),actions=(("modifyPartCollision","collide",True),
                                                      ("modifyPartCollision","physical",False),
                                                      ("call","atConnect", self.touchedSpaz)))                                                                             

        # self.aimZoneObject = bs.Material()
        # self.aimZoneObject.addActions(conditions=(('theyHaveMaterial', bs.getSharedObject('objectMaterial'))),actions=(("modifyPartCollision","collide",True),
                                                      # ("modifyPartCollision","physical",False),
                                                      # ("call","atConnect", self.touchedObject)))

        bs.playSound(bs.getSound('Aim'),position = self.whoControl.position)
        
        self.lookForSpaz()
        
    def lookForSpaz(self):
        self.whoControl.extraAcceleration = (0,20,0)
        self.node = bs.newNode('region',
                       attrs={'position':(self.whoControl.position[0],self.whoControl.position[1],self.whoControl.position[2]) if self.whoControl.exists() else (0,0,0),
                              'scale':(0.0,0.0,0.0),
                              'type':'sphere',
                              'materials':[self.aimZoneSpaz]})
        self.s = bsUtils.animateArray(self.node,"scale",3,{0:(0.0,0.0,0.0),100:(60,60,60)})
        def explode():
            if not self.owner.exists():
                bs.Blast(position = self.whoControl.position,blastRadius = 0.3).autoRetain()
                self.whoControl.handleMessage(bs.DieMessage())
        bs.gameTimer(150,self.node.delete)
        bs.gameTimer(50,explode)
        def checkTarget():
            if self.target is None:
                explode()
            else:
                self.touchedSpaz()
        bs.gameTimer(151,checkTarget)
        
    # def lookForObject(self):
        
        # self.whoControl.extraAcceleration = (0,20,0)
        # self.node2 = bs.newNode('region',
                       # attrs={'position':(self.whoControl.position[0],self.whoControl.position[1],self.whoControl.position[2]) if self.whoControl.exists() else (0,0,0),
                              # 'scale':(0.0,0.0,0.0),
                              # 'type':'sphere',
                              # 'materials':[self.aimZoneObject]})
        # self.s = bsUtils.animateArray(self.node2,"scale",3,{0:(0.0,0.0,0.0),100:(60,60,60)})
        # def explode():
            # if not self.owner.exists():
                # bs.Blast(position = self.whoControl.position,blastRadius = 0.3).autoRetain()
                # self.whoControl.handleMessage(bs.DieMessage())
        # bs.gameTimer(150,self.node2.delete)
        # bs.gameTimer(50,explode)
        # def checkTarget():
            # if self.target is None:
                # if not self.owner.exists():
                    # bs.Blast(position = self.whoControl.position,blastRadius = 0.3).autoRetain()
                    # self.whoControl.handleMessage(bs.DieMessage())
            # else:
                # self.touchedObject()
        # bs.gameTimer(151,checkTarget)
        
    def go(self):
        if self.target is not None and self.whoControl is not None and self.whoControl.exists():
            self.whoControl.velocity = (self.whoControl.velocity[0]+(self.target.position[0]-self.whoControl.position[0]),
                                        self.whoControl.velocity[1]+(self.target.position[1]-self.whoControl.position[1]),
                                        self.whoControl.velocity[2]+(self.target.position[2]-self.whoControl.position[2]))
            bs.gameTimer(1,self.go)
            
    def touchedSpaz(self):
        node = bs.getCollisionInfo('opposingNode')
        if not node == self.owner and node.getDelegate().isAlive():
            self.target = node
            self.s = None
            self.node.delete()
            self.whoControl.extraAcceleration = (0,20,0)
            self.go()
            
    # def touchedObject(self):
        # node = bs.getCollisionInfo('opposingNode')
        # if node.exists() and node.getNodeType() != 'terrain':
            # self.target = node
            # self.s = None
            # self.node.delete()
            # self.whoControl.extraAcceleration = (0,20,0)
            # self.go()
            
    def off(self):
        def sa():
            self.target = None
        bs.gameTimer(100,sa)


class AutoAim2(object):
    def __init__(self,whoControl,owner,aliveOnly = True):
        
        self.whoControl = whoControl
        self.owner = owner
        self.aliveOnly = aliveOnly
        self.target = None
        
        self.aimZoneSpaz = bs.Material()
        self.aimZoneSpaz.addActions(conditions=(('theyHaveMaterial', bs.getSharedObject('playerMaterial'))),actions=(("modifyPartCollision","collide",True),
                                                      ("modifyPartCollision","physical",False),
                                                      ("call","atConnect", self.touchedSpaz)))                                                                             

        # self.aimZoneObject = bs.Material()
        # self.aimZoneObject.addActions(conditions=(('theyHaveMaterial', bs.getSharedObject('objectMaterial'))),actions=(("modifyPartCollision","collide",True),
                                                      # ("modifyPartCollision","physical",False),
                                                      # ("call","atConnect", self.touchedObject)))

        bs.playSound(bs.getSound('Aim'),position = self.whoControl.position)
        
        self.lookForSpaz()
        
    def lookForSpaz(self):
        self.whoControl.extraAcceleration = (0,100,0)
        self.node = bs.newNode('region',
                       attrs={'position':(self.whoControl.position[0],self.whoControl.position[1],self.whoControl.position[2]) if self.whoControl.exists() else (0,0,0),
                              'scale':(0.0,0.0,0.0),
                              'type':'sphere',
                              'materials':[self.aimZoneSpaz]})
        self.s = bsUtils.animateArray(self.node,"scale",3,{0:(0.0,0.0,0.0),100:(60,60,60)})
        def explode():
            if not self.owner.exists():
                bs.Blast(position = self.whoControl.position,blastRadius = 0.3).autoRetain()
                self.whoControl.handleMessage(bs.DieMessage())
        bs.gameTimer(150,self.node.delete)
        bs.gameTimer(50,explode)
        def checkTarget():
            if self.target is None:
                explode()
            else:
                self.touchedSpaz()
        bs.gameTimer(151,checkTarget)
        
    # def lookForObject(self):
        
        # self.whoControl.extraAcceleration = (0,20,0)
        # self.node2 = bs.newNode('region',
                       # attrs={'position':(self.whoControl.position[0],self.whoControl.position[1],self.whoControl.position[2]) if self.whoControl.exists() else (0,0,0),
                              # 'scale':(0.0,0.0,0.0),
                              # 'type':'sphere',
                              # 'materials':[self.aimZoneObject]})
        # self.s = bsUtils.animateArray(self.node2,"scale",3,{0:(0.0,0.0,0.0),100:(60,60,60)})
        # def explode():
            # if not self.owner.exists():
                # bs.Blast(position = self.whoControl.position,blastRadius = 0.3).autoRetain()
                # self.whoControl.handleMessage(bs.DieMessage())
        # bs.gameTimer(150,self.node2.delete)
        # bs.gameTimer(50,explode)
        # def checkTarget():
            # if self.target is None:
                # if not self.owner.exists():
                    # bs.Blast(position = self.whoControl.position,blastRadius = 0.3).autoRetain()
                    # self.whoControl.handleMessage(bs.DieMessage())
            # else:
                # self.touchedObject()
        # bs.gameTimer(151,checkTarget)
        
    def go(self):
        if self.target is not None and self.whoControl is not None and self.whoControl.exists():
            self.whoControl.velocity = (self.whoControl.velocity[0]+(self.target.position[0]-self.whoControl.position[0]),
                                        self.whoControl.velocity[1]+(self.target.position[1]-self.whoControl.position[1]),
                                        self.whoControl.velocity[2]+(self.target.position[2]-self.whoControl.position[2]))
            bs.gameTimer(1,self.go)
            
    def touchedSpaz(self):
        node = bs.getCollisionInfo('opposingNode')
        if not node == self.owner and node.getDelegate().isAlive():
            self.target = node
            self.s = None
            self.node.delete()
            self.whoControl.extraAcceleration = (0,70,0)
            self.go()
            
    # def touchedObject(self):
        # node = bs.getCollisionInfo('opposingNode')
        # if node.exists() and node.getNodeType() != 'terrain':
            # self.target = node
            # self.s = None
            # self.node.delete()
            # self.whoControl.extraAcceleration = (0,20,0)
            # self.go()
            
    def off(self):
        def sa():
            self.target = None
        bs.gameTimer(100,sa)
