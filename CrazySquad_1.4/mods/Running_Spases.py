#Made by SEBASTIAN2059
import bs, bsSpaz, random
from bsSpaz import*

def bsGetAPIVersion():
    return 4

def bsGetGames():
    return [RunningSpases1Game]


###############  SPAZ   ##################
t = Appearance("Spaz2")

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

t.jumpSounds=[]
t.attackSounds=[]
t.impactSounds=[]
t.deathSounds=[]
t.pickupSounds=[]
t.fallSounds=[]

t.style = 'spaz'

##########New Bot##########
class BotType1(bsSpaz.ToughGuyBot):
    """
    category: Bot Classes
    
    A less aggressive yellow version of bs.ToughGuyBot.
    """
    color=(1,1,1)
    highlight=(1,1,1)
    character = 'Spaz2'
    punchiness = 0.3
    chargeSpeedMin = 0 #0.6
    chargeSpeedMax = 0 #0.6
    chargeDistMax = 0
    throwDistMin = 0 #9999
    throwDistMax = 0 #9999

       
    def handleMessage(self,m):
        super(self.__class__, self).handleMessage(m)
        self._nameColor = bs.Timer(10,bs.WeakCall(self._impulse),repeat=True)
        self._deadBot = bs.Timer(3500,bs.WeakCall(self._deadBot),repeat=False)
        self._color = bs.Timer(10,bs.WeakCall(self._color),repeat=False)

    def _impulse(self):
        self.node.handleMessage(
                            'impulse',
                            self.node.position[0],
                            self.node.position[1]+5,
                            self.node.position[2],
                            0, 0, 0, 5, 0, 0, 0, -6500, 0, 0)
        self.node.handleMessage('knockout',5000)

    def _color(self):
        self.node.color=(random.random()*2,random.random()*2,random.random()*2)
                
    def _deadBot(self):
        self.handleMessage(bs.DieMessage(immediate=True))
        
class BotType2(bsSpaz.ToughGuyBot):
    color=(1,1,1)
    highlight=(1,1,1)
    character = 'Spaz2'
    punchiness = 0.3
    chargeSpeedMin = 0 #0.6
    chargeSpeedMax = 0 #0.6
    chargeDistMax = 0
    throwDistMin = 0 #9999
    throwDistMax = 0 #9999

       
    def handleMessage(self,m):
        super(self.__class__, self).handleMessage(m)
        self._nameColor = bs.Timer(10,bs.WeakCall(self._impulse),repeat=True)
        self._deadBot = bs.Timer(3500,bs.WeakCall(self._deadBot),repeat=False)
        self._color = bs.Timer(10,bs.WeakCall(self._color),repeat=False)

    def _impulse(self):
        self.node.handleMessage(
                            'impulse',
                            self.node.position[0],
                            self.node.position[1]+5,
                            self.node.position[2],
                            0, 0, 0, 5, 0, 0, 0, 6500, 0, 0)
        self.node.handleMessage('knockout',5000)

    def _color(self):
        self.node.color=(random.random()*2,random.random()*2,random.random()*2)
                
    def _deadBot(self):
        self.handleMessage(bs.DieMessage(immediate=True))        
	
class RunningSpases1Game(bs.TeamGameActivity):

    @classmethod
    def getName(cls):
        return 'Running Spases'

    @classmethod
    def getScoreInfo(cls):
        return {'scoreName':'Survived',
                'scoreType':'milliseconds',
                'scoreVersion':'B'}
    
    @classmethod
    def getDescription(cls,sessionType):
        return 'Pero que esta pasando?\nEl suelo esta muy resbaloso.'

    @classmethod
    def getSupportedMaps(cls,sessionType):
        return ['Football Stadium']

    @classmethod
    def getSettings(cls,sessionType):
        return [("Epic Mode",{'default':False}),
                ("Dificultad",{'minValue':1,'maxValue':3,'default':1,'increment':1}),
                ("Direccion",{'choices': [(bs.getSpecialChar('leftArrow'), 1),(bs.getSpecialChar('rightArrow'), 2)],'default': 1})]

    @classmethod
    def supportsSessionType(cls,sessionType):
        return True if (issubclass(sessionType,bs.TeamsSession)
                        or issubclass(sessionType,bs.FreeForAllSession)
                        or issubclass(sessionType,bs.CoopSession)) else False

    def __init__(self,settings):
        bs.TeamGameActivity.__init__(self,settings)
        if self.settings['Epic Mode']: self._isSlowMotion = True
        self.announcePlayerDeaths = True
        self._lastPlayerDeathTime = None
        
        #prevent a safe zone from player              
        self.killPlayerRegionMaterial = bs.Material()
        self.killPlayerRegionMaterial.addActions(
            conditions=("theyHaveMaterial",bs.getSharedObject('playerMaterial')),
            actions=(("modifyPartCollision","collide",True),
                     ("modifyPartCollision","physical",False),
                     ("call","atConnect",self._killPlayer)))

        # we need this region because if not exists, the bombs creates a earthquake XD
        self.killBombRegionMaterial = bs.Material()
        self.killBombRegionMaterial.addActions(
            conditions=("theyHaveMaterial",bs.Bomb.getFactory().bombMaterial),
            actions=(("modifyPartCollision","collide",True),
                     ("modifyPartCollision","physical",False),
                     ("call","atConnect",self._killBomb)))

    def onTransitionIn(self):
        bs.TeamGameActivity.onTransitionIn(self, music='Epic' if self.settings['Epic Mode'] else 'Survival')
        bs.getSharedObject('globals').tint = (1.2,1.0,1.0)
        self.iceMaterial = bs.Material()
        self.iceMaterial.addActions(actions=('modifyPartCollision','friction',0.003))
        bs.getActivity().getMap().node.materials = [bs.getSharedObject('footingMaterial'),self.iceMaterial]
        #bs.getActivity().getMap().node.color= (0,0,0)
        #bs.getActivity().getMap().node.reflection = 'soft'
        #bs.getActivity().getMap().node.reflectionScale = [1]
        
        # a = bs.newNode('locator',attrs={'shape':'box','position':(12,0,.1087926362),
            # 'color':(5,5,5),'opacity':1,'drawBeauty':True,'additive':False,'size':[2.0,0.1,11.8]})
            
        #b = bs.newNode('locator',attrs={'shape':'box','position':(-12,0,.1087926362),
            #'color':(5,5,5),'opacity':1,'drawBeauty':True,'additive':False,'size':[2.0,0.1,11.8]})
		
    def onPlayerJoin(self, player):
        if self.hasBegun():
            bs.screenMessage(
                bs.Lstr(
                    resource='playerDelayedJoinText',
                    subs=[('${PLAYER}', player.getName(full=True))]),
                color=(0, 1, 0))
            player.gameData['deathTime'] = self._timer.getStartTime()
            return
        self.spawnPlayer(player)

    def onPlayerLeave(self, player):
        bs.TeamGameActivity.onPlayerLeave(self, player)
        self._checkEndGame()

    def onBegin(self):
        bs.TeamGameActivity.onBegin(self)
# set up the two score regions
        self._scoreRegions = []

        defs = self.getMap().defs
        self._scoreRegions.append(bs.NodeActor(bs.newNode('region',
                                                          attrs={'position':defs.boxes['goal1'][0:3],
                                                                 'scale':defs.boxes['goal1'][6:9],
                                                                 'type': 'box',
                                                                 'materials':(self.killPlayerRegionMaterial,)})))
        
        self._scoreRegions.append(bs.NodeActor(bs.newNode('region',
                                                          attrs={'position':defs.boxes['goal2'][0:3],
                                                                 'scale':defs.boxes['goal2'][6:9],
                                                                 'type': 'box',
                                                                 'materials':(self.killBombRegionMaterial,self.killPlayerRegionMaterial)})))
                                                                 
        bs.gameTimer(4000,self.start)
        self._bots = bs.BotSet()
		
        self._timer = bs.OnScreenTimer()
        bs.gameTimer(4000,self._timer.start)
        #self._timer.start()
        
    def spawnPlayer(self,player):
        spaz = self.spawnPlayerSpaz(player)
        spaz.connectControlsToPlayer(enablePunch=False,
                                     enableBomb=False,
                                     enablePickUp=False)
        spaz.playBigDeathSound = True

    def _killPlayer(self):
        regionNode,playerNode = bs.getCollisionInfo('sourceNode','opposingNode')
        try: player = playerNode.getDelegate().getPlayer()
        except Exception: player = None
        region = regionNode.getDelegate()
        if player.exists():
         player.actor.handleMessage(bs.DieMessage())
         player.actor.shatter()

    def _killBomb(self):
        regionNode,bombNode = bs.getCollisionInfo('sourceNode','opposingNode')
        try: bomb = bombNode.getDelegate()
        except Exception: bomb = None
        region = regionNode.getDelegate()
        if bomb.exists():
         bomb.handleMessage(bs.DieMessage())
         
    def handleMessage(self,m):
        if isinstance(m,bs.PlayerSpazDeathMessage):
            bs.TeamGameActivity.handleMessage(self,m)
            deathTime = bs.getGameTime()
            m.spaz.getPlayer().gameData['deathTime'] = deathTime
            if isinstance(self.getSession(),bs.CoopSession):
                bs.pushCall(self._checkEndGame)
                self._lastPlayerDeathTime = deathTime
            else: bs.gameTimer(1000,self._checkEndGame)
        else:  bs.TeamGameActivity.handleMessage(self,m)

    def _checkEndGame(self):
        livingTeamCount = 0
        for team in self.teams:
            for player in team.players:
                if player.isAlive():
                    livingTeamCount += 1
                    break
        if isinstance(self.getSession(),bs.CoopSession):
            if livingTeamCount <= 0: self.endGame()
        else:
            if livingTeamCount <= 1: self.endGame()
			
    def start(self):
        if self.settings['Dificultad'] == 1:
            bs.gameTimer(300,bs.Call(self._decTime),repeat=True)
        elif self.settings['Dificultad'] == 2:
            bs.gameTimer(200,bs.Call(self._decTime),repeat=True)
        elif self.settings['Dificultad'] == 3:
            bs.gameTimer(100,bs.Call(self._decTime),repeat=True)
    
    def _decTime(self):
        x = [-5.5,-5,-4.5,-4,-3.5,-3,-2.5,-2,-1.5,-1,-0.5,0,0.5,1,1.5,2,2.5,3,3.5,4,4.5,5,5.5,5.7]
        pos=(13.4,1,random.choice(x))
        pos2=(-13.4,1,random.choice(x))
        if self.settings['Direccion'] == 1:
            self._bots.spawnBot(BotType1,pos=pos,spawnTime=0)
        if self.settings['Direccion'] == 2:
            self._bots.spawnBot(BotType2,pos=pos2,spawnTime=0)

    def endGame(self):
        curTime = bs.getGameTime()
        for team in self.teams:
            for player in team.players:
                if 'deathTime' not in player.gameData: player.gameData['deathTime'] = curTime+1
                score = (player.gameData['deathTime']-self._timer.getStartTime())/1000
                if 'deathTime' not in player.gameData: score += 50
                self.scoreSet.playerScored(player,score,screenMessage=False)
        self._timer.stop(endTime=self._lastPlayerDeathTime)
        results = bs.TeamGameResults()
        for team in self.teams:
            longestLife = 0
            for player in team.players:
                longestLife = max(longestLife,(player.gameData['deathTime'] - self._timer.getStartTime()))
            results.setTeamScore(team,longestLife)
        self.end(results=results)