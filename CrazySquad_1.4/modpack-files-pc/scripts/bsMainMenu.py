import bs
import bsUtils
import bsUI
import bsSpaz
import random
import time
import weakref
import bsInternal
import settings
from bsTheme import*

gDidInitialTransition = False
gStartTime = time.time()
    
class MainMenuActivity(bs.Activity):

    def __init__(self, settings={}):
        bs.Activity.__init__(self,settings)

    def onTransitionIn(self):
        import bsInternal
        bs.Activity.onTransitionIn(self)
        global gDidInitialTransition
        random.seed(123)
        self._logoNode = None
        self._customLogoTexName = None
        self._wordActors = []
        env = bs.getEnvironment()
                
        if not gDidInitialTransition:
            bs.getConfig()['Activate'] = False
            
        # FIXME - shouldn't be doing things conditionally based on whether
        # the host is vr mode or not (clients may not be or vice versa) -
        # any differences need to happen at the engine level
        # so everyone sees things in their own optimal way
        vrMode = bs.getEnvironment()['vrMode']

        if not bs.getEnvironment().get('toolbarTest', True):
            self.myName = bs.NodeActor(bs.newNode('text', attrs={
                'vAttach':'bottom',
                'hAlign':'center',
                'color':(0,1.0,1.0,1.0) if vrMode else gInfoTextColor,
                'flatness':1.0,
                'shadow':1.0 if vrMode else 0.5,
                'scale':(0.9 if (env['interfaceType'] == 'small' or vrMode)
                         else 0.7), # FIXME need a node attr for this
                'position':(0,10),
                'vrDepth':-10,
                'text':u'\xa9 2018 Eric Froemling - SEBASTIAN2059'}))
        
        # throw up some text that only clients can see so they know that the
        # host is navigating menus while they're just staring at an
        # empty-ish screen..
        self._hostIsNavigatingText = bs.NodeActor(bs.newNode('text', attrs={
            'text':bs.Lstr(resource='hostIsNavigatingMenusText',
                           subs=[('${HOST}',
                                  bsInternal._getAccountDisplayString())]),
            'clientOnly':True,
            'position':(0,-200),
            'flatness':1.0,
            'hAlign':'center'}))
        if not gDidInitialTransition and hasattr(self,'myName'):
            bs.animate(self.myName.node, 'opacity', {2300:0,3000:1.0})

        # TEMP - testing hindi text
        if False:
            # bs.screenMessage("TESTING: "+'TST: "deivit \xf0\x9f\x90\xa2"')
            self.tTest = bs.NodeActor(bs.newNode('text', attrs={
                'vAttach':'center',
                'hAlign':'left',
                'color':(0,1,1,1),
                'shadow':1.0,
                'flatness':0.0,
                'scale':1,
                'position':(-500,-40),
                'text':('\xe0\xa4\x9c\xe0\xa4\xbf\xe0\xa4\xb8 \xe0\xa4\xad'
                        '\xe0\xa5\x80 \xe0\xa4\x9a\xe0\xa5\x80\xe0\xa5\x9b '
                        '\xe0\xa4\x95\xe0\xa5\x8b \xe0\xa4\x9b\xe0\xa5\x81'
                        '\xe0\xa4\x8f\xe0\xa4\x81\xe0\xa4\x97\xe0\xa5\x87 '
                        '\xe0\xa4\x89\xe0\xa4\xb8\xe0\xa4\xb8\xe0\xa5\x87 '
                        '\xe0\xa4\x9a\xe0\xa4\xbf\xe0\xa4\xaa\xe0\xa4\x95'
                        '\n\xe0\xa4\x9c\xe0\xa4\xbe\xe0\xa4\xaf\xe0\xa5\x87'
                        '\xe0\xa4\x82\xe0\xa4\x97\xe0\xa5\x87 .. \xe0\xa4'
                        '\x87\xe0\xa4\xb8\xe0\xa4\x95\xe0\xa4\xbe \xe0\xa4'
                        '\xae\xe0\xa5\x9b\xe0\xa4\xbe \xe0\xa4\xb2\xe0\xa5'
                        '\x87\xe0\xa4\x82 !')}))
        # TEMP - test emoji
        if False:
            # bs.screenMessage("TESTING: "+'TST: "deivit \xf0\x9f\x90\xa2"')
            self.tTest = bs.NodeActor(bs.newNode('text', attrs={
                'vAttach':'center',
                'hAlign':'left',
                'color':(0,1,1,1),
                'shadow':1.0,
                'flatness':1.0,
                'scale':1,
                'position':(-500,-40),
                'text':('TST: "deivit \xf0\x9f\x90\xa2"')}))
        # TEMP - testing something; forgot what
        if False:
            # bs.screenMessage("TESTING: "+'TST: "deivit \xf0\x9f\x90\xa2"')
            self.tTest = bs.NodeActor(bs.newNode('text', attrs={
                'vAttach':'center',
                'hAlign':'left',
                'color':(0,1,1,1),
                'shadow':1.0,
                'flatness':0.0,
                'scale':1,
                'position':(-500,0),
                'text':u('        \u3147\u3147                             '
                         '            \uad8c\ucc2c\uadfc                   '
                         '                        \uae40\uc6d0\uc7ac\n     '
                         '   \ub10c                                        '
                         '    \uc804\uac10\ud638\nlll\u0935\u093f\u0936\u0947'
                         '\u0937 \u0927\u0928\u094d\u092f\u0935\u093e'
                         '\u0926:\n')}))
        # TEMP - test chinese text
        if False:
            self.tTest = bs.NodeActor(bs.newNode('text', attrs={
                'vAttach':'center',
                'hAlign':'center',
                'color':(0,1,1,1),
                'shadow':1.0,
                'flatness':0.0,
                'scale':1,
                'position':(-400,-40),
                'text':('TST: "\xe8\x8e\xb7\xe5\x8f\x96\xe6\x9b\xb4\xe5\xa4'
                        '\x9a\xe5\x9b\xbe\xe6\xa0\x87"\n\xe6\x88\x90\xe5'
                        '\xb0\xb1\xe4\xb8\xad|         foo\n\xe8\xb4\xa6'
                        '\xe6\x88\xb7 \xe7\x99\xbb\xe9\x99\x86foo\nend"'
                        '\xe8\x8e\xb7\xe5\x8f\x96\xe6\x9b\xb4\xe5\xa4\x9a'
                        '\xe5\x9b\xbe\xe6\xa0\x87"\nend"\xe8\x8e\xb7\xe5'
                        '\x8f\x96\xe6\x9b\xb4\xe5\xa4\x9a\xe5\x9b\xbe\xe6'
                        '\xa0\x87"\nend2"\xe8\x8e\xb7\xe5\x8f\x96\xe6\x9b'
                        '\xb4\xe5\xa4\x9a\xe5\x9b\xbe\xe6\xa0\x87"\n')}))

        # FIXME - shouldn't be doing things conditionally based on whether
        # the host is vr mode or not (clients may not be or vice versa)
        # - any differences need to happen at the engine level
        # so everyone sees things in their own optimal way
        vrMode = env['vrMode']
        interfaceType = env['interfaceType']

        # in cases where we're doing lots of dev work lets
        # always show the build number
        forceShowBuildNumber = False

        if not bs.getEnvironment().get('toolbarTest', True):
            if env['debugBuild'] or env['testBuild'] or forceShowBuildNumber:
                if env['debugBuild']:
                    text = bs.Lstr(value='${V} (${B}) (${D})',
                                   subs=[('${V}', env['version']),
                                         ('${B}', str(env['buildNumber'])),
                                         ('${D}',bs.Lstr(resource='debugText')
                                         )])
                else:
                    text = bs.Lstr(value='${V} (${B})',
                                   subs=[('${V}', env['version']),
                                         ('${B}', str(env['buildNumber']))])
            else:
                text = bs.Lstr(value='${V}', subs=[('${V}', env['version'])])
            self.version = bs.NodeActor(bs.newNode('text', attrs={
                'vAttach':'bottom',
                'hAttach':'right',
                'hAlign':'right',
                'flatness':1.0,
                'vrDepth':-10,
                'shadow':1.0 if vrMode else 0.5,
                'color':(0,1,1,1) if vrMode else gInfoTextColor,
                'scale':0.9 if (interfaceType == 'small' or vrMode) else 0.7,
                'position':(-260,10) if vrMode else (-10,10),
                'text':'v2.0(Beta)'}))
            if not gDidInitialTransition:
                bs.animate(self.version.node,'opacity',{2300:0,3000:1.0})
            
        # throw in beta info..
        self.betaInfo = self.betaInfo2 = None
        if env['testBuild'] and not env['kioskMode']:
            self.betaInfo = bs.NodeActor(bs.newNode('text', attrs={
                'vAttach':'center',
                'hAlign':'center',
                'color':(0,1,1,1),
                'shadow':0.5,
                'flatness':0.5,
                'scale':0,
                'vrDepth':-60,
                'position':(230,125) if env['kioskMode'] else (230,35),
                'text':bs.Lstr(resource='testBuildText')}))
            if not gDidInitialTransition:
                bs.animate(self.betaInfo.node,'opacity',{1300:0,1800:1.0})

            
        model = bs.getModel('thePadLevel')
        collide = bs.getCollideModel('thePadLevelCollide')
        treesModel = bs.getModel('trees')
        bottomModel = bs.getModel('thePadLevelBottom')
        testColorTexture = bs.getTexture('thePadLevelColor')
        treesTexture = bs.getTexture('treesColor') 
        
        import bsMap
        self._map = bsMap.ThePadMap
        self._map.isHockey = False

        #menuBG
        bgTex = bs.getTexture('menuBG')
        bgTex2 = bs.getTexture('fondoColores')
        bgTex3 = bs.getTexture('galaxiafondo')
       #if settings.menuTex == 0:
       	 #bgTex = bs.getTexture('fondoColores')
        #elif settings.menuTex == 1:
       	 #bgTex = bs.getTexture('menuBG')
       
        bgModel = bs.getModel('thePadBG')
                
        if settings.menuEvent == 0:
       	 None
        elif settings.menuEvent == 1:
       	 self._bombRain = bs.Timer(1000,bs.WeakCall(self.dropB),repeat = True)
       	 self._bomb1Rain = bs.Timer(1200,bs.WeakCall(self.dropB1),repeat = True)
       	 self._bomb2Rain = bs.Timer(1400,bs.WeakCall(self.dropB2),repeat = True)
       	 self._bomb3Rain = bs.Timer(1800,bs.WeakCall(self.dropB3),repeat = True)
       	 self._bomb4Rain = bs.Timer(2000,bs.WeakCall(self.dropB4),repeat = True)
       	 self._bomb5Rain = bs.Timer(2200,bs.WeakCall(self.dropB5),repeat = True)
       	 self._bomb6Rain = bs.Timer(2400,bs.WeakCall(self.dropB6),repeat = True)
       	 self._bomb7Rain = bs.Timer(2600,bs.WeakCall(self.dropB7),repeat = True)
        elif settings.menuEvent == 2:
       	 self._powerupRain = bs.Timer(int(random.choice([150,170])),bs.WeakCall(self.dropP),repeat = True)


        # (load these last since most platforms don't use them..)
        vrBottomFillModel = bs.getModel('thePadVRFillBottom')
        vrTopFillModel = bs.getModel('thePadVRFillTop')
        
        bsGlobals = bs.getSharedObject('globals')
        #bsGlobals.cameraMode = 'rotate' #settings.cameraMode
        bsGlobals.slowMotion = settings.slowMotion
        
        if settings.cameraMode == 0:
       	 bsGlobals.cameraMode = 'rotate'
        elif settings.cameraMode == 1:
       	 bsGlobals.cameraMode = 'follow'

        #tint = (1.1,1.1,1)
        #bsGlobals.tint = tint        
        if settings.tintColor == 'Auto':
       	 bsGlobals.tint = (1.1,1.1,1)
        elif settings.tintColor == 'Red':
       	 bsGlobals.tint = (1,0,0)
        elif settings.tintColor == 'Green':
       	 bsGlobals.tint = (0,1,0)
        elif settings.tintColor == 'Blue':
       	 bsGlobals.tint = (0,0,1)
        elif settings.tintColor == 'Sunset':
       	 bsGlobals.tint = (0.8,0.6,0.4)
        elif settings.tintColor == 'Night':
       	 bsGlobals.tint = (0.23,0.23,0.23*2)
        elif settings.tintColor == 'Radioactive':
       	 bsGlobals.tint = (0.4,0.6,0.2)

        #bsUtils.animateArray(bs.getSharedObject('globals'),'tint',3,{0:(0.7,0.7,0.7),10000:(1.1,1.1,1),15000:(1.1,1.1,1),20000:(0.5,0.5,0.5),25000:(0.2,0.2,0.27),30000:(0.2,0.2,0.27),35000:(0.5,0.5,0.5),40000:(1.1,1.1,1),45000:(1.1,1.1,1),50000:(0.5,0.5,0.5),55000:(0.2,0.2,0.27),60000:(0.2,0.2,0.27),65000:(0.5,0.5,0.5),70000:(0.7,0.7,0.7),75000:(1.1,1.1,1),80000:(1.5,1.5,0.8),85000:(1.5,0.8,0.8),90000:(1.2,0.2,0.2),95000:(1.2,0,0),100000:(1.2,0.5,0),105000:(0.6,0.5,0),110000:(0.2,0.2,0.3),115000:(0.2,0.2,0.3)})
        #bsUtils.animateArray(bs.getSharedObject('globals'),'ambientColor',3,{0:(4.0,0.0,0.0),1000:(0.0,4.0,0),1500:(0,0,4),2000:(4,4,0),2500:(4,0,4),4000:(0,4,4),4500:(4,0,0)},True)
            
        bsGlobals.ambientColor = (1,1,1)
        bsGlobals.vignetteOuter = (0.45, 0.55, 0.54)
        bsGlobals.vignetteInner = (0.95, 0.95, 0.93)
        settings.map = 1 if settings.event == 'event_0' or settings.event == 'event_2' or settings.event == 'event_3' or settings.event == 'event_4' or settings.event == 'event_6' else 0
        settings.bg = 1 if settings.event == 'event_5' else 0
        
                            
        if settings.map == 0:
        	None
      	  #self.bg = bs.NodeActor(bs.newNode('terrain', attrs={
           	  #'model':bgModel,
           	  #'color':(0.92,0.91,0.9),
           	  #'lighting':False,
    	         #'background':True,
          	   #'colorTexture':bgTex}))

        if settings.map == 1:
      	  self.bottom = bs.NodeActor(bs.newNode('terrain', attrs={
           	  'model':bottomModel,
           	  'lighting':False,
           	  'reflection':'soft',
           	  'reflectionScale':[0.45],
           	  'colorTexture':testColorTexture}))
      	  self.collide = bs.NodeActor(bs.newNode('terrain',attrs={
           	  'collideModel':collide,
           	  'lighting':False,
           	  'reflection':'soft',
           	  'reflectionScale':[0.45],
           	  'colorTexture':testColorTexture}))
      	  self.vrBottomFill = bs.NodeActor(bs.newNode('terrain', attrs={
           	  'model':vrBottomFillModel,
           	  'lighting':False,
           	  'vrOnly':True,
           	  'colorTexture':testColorTexture}))
      	  self.vrTopFill = bs.NodeActor(bs.newNode('terrain', attrs={
           	  'model':vrTopFillModel,
           	  'vrOnly':True,
           	  'lighting':False,
           	  'colorTexture':bgTex}))
      	  self.terrain = bs.NodeActor(bs.newNode('terrain', attrs={
           	  'model': model,
           	  'collideModel': collide,
           	  'colorTexture': testColorTexture,
           	  'reflection': 'soft',
           	  'reflectionScale': [0.3],
           	  'materials': [bs.getSharedObject('footingMaterial')]}))
      	  self.trees = bs.NodeActor(bs.newNode('terrain', attrs={
           	  'model':treesModel,
           	  'lighting':False,
           	  'reflection':'char',
           	  'reflectionScale':[0.1],
           	  'colorTexture':treesTexture}))
      	  self.bg = bs.NodeActor(bs.newNode('terrain', attrs={
           	  'model':bgModel,
           	  'color':(0.92,0.91,0.9),
           	  'lighting':False,
    	         'background':True,
          	   'colorTexture':bgTex}))
                                      
        if settings.bg == 0:
      	  self.bg = bs.NodeActor(bs.newNode('terrain', attrs={
           	  'model':bgModel,
           	  'color':(0.92,0.91,0.9),
           	  'lighting':False,
    	         'background':True,
          	   'colorTexture':bgTex}))
                                                
        if settings.bg == 1:
      	  self.bg = bs.NodeActor(bs.newNode('terrain', attrs={
           	  'model':bgModel,
           	  'color':(0.92,0.91,0.9),
           	  'lighting':False,
    	         'background':True,
          	   'colorTexture':bgTex2}))
          
        textOffsetV = 0
        self._ts = 0.86

        self._language = None
        self._updateTimer = bs.Timer(1000, self._update, repeat=True)
        self._update()

        # hopefully this won't hitch but lets space these out anyway..
        bsInternal._addCleanFrameCallback(bs.WeakCall(self._startPreloads))
        
			#Eventos#
        if settings.event == 'event_0':
            None
              
        elif settings.event == 'event_1':
            bsGlobals.ambientColor = (0.8, 1.3, 0.8)
            bsGlobals.vignetteOuter = (0.8, 0.8, 0.8)
            bsGlobals.vignetteInner = (10, 1, 1)
            bsGlobals.cameraMode = 'follow'
            tint = (0.75, 0.75, 0.75)
            self.color = (1, 1, 1)

            # play standart music
            #bs.playMusic('Menu')

            def spawnCCube():
                pos = (15, random.uniform(2, 8), random.uniform(4, -10))
                if not random.random() > 0.9997:
                    cC = bs.Powerup(position=pos,powerupType=bs.Powerup.getFactory().getRandomPowerupType()).autoRetain()

                    cC.node.extraAcceleration = (0, 20, 0)
                    cC.node.velocity = (random.random()*-10,
                                        random.random()*3,
                                        random.random()*3)


            bs.gameTimer(50, bs.Call(spawnCCube), repeat=True)
            
        elif settings.event == 'event_2':
            bsGlobals.ambientColor = (0.8, 1.3, 0.8)
            bsGlobals.vignetteOuter = (0.8, 0.8, 0.8)
            bsGlobals.vignetteInner = (1, 1, 1)
            #bsGlobals.cameraMode = 'follow'
            tint = (1.14, 1.1, 1.0)
            self.color = (1, 1, 1)
            settings.map = 1
            settings.saveSettings()
            
            # play standart music
            #bs.playMusic('Menu')
            
                                
            self._floatText = bs.newNode(
                'text',
                attrs={
                    'text':bs.Lstr(resource='characterText'),
                    'position':(0,3.7,4),
                    'color':(1,1,1),
                    'inWorld': True,
                    'scale':0.0225,
                    'hAlign': 'center'
                })
            
###################################

            self._spazArray = []
            s = bs.Spaz(color=(0.5, 0.25, 1),highlight = (0.5, 0.25, 1),character='Spaz')
            s.node.name = "Spaz"
            s.node.nameColor = (0.5, 0.25, 1)
            s.node.handleMessage(bs.StandMessage(position=(-1.5,2.6,-7)))
            self._spazArray.append(s)
            
            self._spazArray0 = []
            s = bs.Spaz(color=(0.6, 0.6, 0.6),highlight = (0, 1, 0),character='Zoe')
            s.node.name = "Zoe"
            s.node.nameColor = (0.6,0.6,0.6)
            s.node.handleMessage(bs.StandMessage(position=(1.5,2.6,-7)))
            self._spazArray0.append(s)
               
            self._spazArray2 = []
            s = bs.Spaz(color=(1, 1, 1),highlight = (0.55, 0.8, 0.55),character='Snake Shadow')
            s.node.name = "Snake Shadow"
            s.node.nameColor = (1,1,1)
            s.node.handleMessage(bs.StandMessage(position=(1.5,2.6,-1)))
            self._spazArray2.append(s)
            
            self._spazArray3 = []
            s = bs.Spaz(color=(0.4, 0.5, 0.4),highlight = (1, 0.5, 0.3),character='Kronk')
            s.node.name = "Kronk"
            s.node.nameColor = (0.4, 0.5, 0.4)
            s.node.handleMessage(bs.StandMessage(position=(0,2.6,-3)))
            self._spazArray3.append(s)
                        
            self._spazArray4 = []
            s = bs.Spaz(color=(1, 1, 1),highlight = (0.1, 0.6, 0.1),character='Mel')
            s.node.name = "Mel"
            s.node.nameColor = (1, 1, 1)
            s.node.handleMessage(bs.StandMessage(position=(-1.5,2.6,-5)))
            self._spazArray4.append(s)
                        
            self._spazArray5 = []
            s = bs.Spaz(color=(1, 0.2, 0.1),highlight = (1, 1, 0),character='Jack Morgan')
            s.node.name = "Jack Morgan"
            s.node.nameColor = (1, 0.2, 0.1)
            s.node.handleMessage(bs.StandMessage(position=(-1.5,2.6,-1)))
            self._spazArray5.append(s)
                        
            self._spazArray6 = []
            s = bs.Spaz(color=(1, 0, 0),highlight = (1, 1, 1),character='Santa Claus')
            s.node.name = "Santa Claus"
            s.node.nameColor = (1, 0, 0)
            s.node.handleMessage(bs.StandMessage(position=(-1.5,2.6,-3)))
            self._spazArray6.append(s)
                        
            self._spazArray7 = []
            s = bs.Spaz(color=(0.5, 0.5, 1),highlight = (1, 0.5, 0),character='Frosty')
            s.node.name = "Frosty"
            s.node.nameColor = (0.5, 0.5, 1)
            s.node.handleMessage(bs.StandMessage(position=(3,2.6,-3)))
            self._spazArray7.append(s)
                                    
            self._spazArray8 = []
            s = bs.Spaz(color=(0.6, 0.9, 1),highlight = (0.6, 0.9, 1),character='Bones')
            s.node.name = "Bones"
            s.node.nameColor = (0.6, 0.9, 1)
            s.node.handleMessage(bs.StandMessage(position=(-3,2.6,-3)))
            self._spazArray8.append(s)
            
            self._spazArray9 = []
            s = bs.Spaz(color=(0.7, 0.5, 0.0),highlight = (0.6, 0.5, 0.8),character='Bernard')
            s.node.name = "Bernard"
            s.node.nameColor = (0.7, 0.5, 0.0)
            s.node.handleMessage(bs.StandMessage(position=(3,2.6,-5)))
            self._spazArray9.append(s)
               
            self._spazArray10 = []
            s = bs.Spaz(color=(0.3, 0.5, 0.8),highlight = (1, 0, 0),character='Pascal')
            s.node.name = "Pascal"
            s.node.nameColor = (0.3, 0.5, 0.8)
            s.node.handleMessage(bs.StandMessage(position=(0,2.6,-5)))
            self._spazArray10.append(s)
            
            self._spazArray11 = []
            s = bs.Spaz(color=(1, 0.5, 0),highlight = (1, 1, 1),character='Taobao Mascot')
            s.node.name = "Taobao Mascot"
            s.node.nameColor = (1, 0.5, 0)
            s.node.handleMessage(bs.StandMessage(position=(0,2.6,-1)))
            self._spazArray11.append(s)
                        
            self._spazArray12 = []
            s = bs.Spaz(color=(0.5, 0.5, 0.5),highlight = (1, 0, 0),character='B-9000')
            s.node.name = "B-9000"
            s.node.nameColor = (0.5, 0.5, 0.5)
            s.node.handleMessage(bs.StandMessage(position=(1.5,2.6,-5)))
            self._spazArray12.append(s)
                        
            self._spazArray13 = []
            s = bs.Spaz(color=(0.3, 0.3, 0.33),highlight = (1, 0.5, 0.3),character='Agent Johnson')
            s.node.name = "Agent Johnson"
            s.node.nameColor = (0.3, 0.3, 0.33)
            s.node.handleMessage(bs.StandMessage(position=(1.5,2.6,-3)))
            self._spazArray13.append(s)
                        
            self._spazArray14 = []
            s = bs.Spaz(color=(0.2, 0.4, 1.0),highlight = (0.06, 0.15, 0.4),character='Grumbledorf')
            s.node.name = "Grumbledorf"
            s.node.nameColor = (0.2, 0.4, 1.0)
            s.node.handleMessage(bs.StandMessage(position=(3,2.6,-1)))
            self._spazArray14.append(s)
                        
            self._spazArray15 = []
            s = bs.Spaz(color=(0, 1, 0.7),highlight = (0.65, 0.35, 0.75),character='Pixel')
            s.node.name = "Pixel"
            s.node.nameColor = (0, 1, 0.7)
            s.node.handleMessage(bs.StandMessage(position=(-3,2.6,-5)))
            self._spazArray15.append(s)
                                    
            self._spazArray16 = []
            s = bs.Spaz(color=(1, 1, 1),highlight = (1, 0.5, 0.5),character='Easter Bunny')
            s.node.name = "Easter Bunny"
            s.node.nameColor = (1, 1, 1)
            s.node.handleMessage(bs.StandMessage(position=(-3,2.6,-1)))
            self._spazArray16.append(s)
            
            def position():
                s = int(random.random() * len(self._spazArray))
                self._spazArray[s].node.moveUpDown = -1
                self._spazArray0[s].node.moveUpDown = -1
                self._spazArray2[s].node.moveUpDown = -1
                self._spazArray3[s].node.moveUpDown = -1
                self._spazArray4[s].node.moveUpDown = -1
                self._spazArray5[s].node.moveUpDown = -1
                self._spazArray6[s].node.moveUpDown = -1
                self._spazArray7[s].node.moveUpDown = -1
                self._spazArray8[s].node.moveUpDown = -1
                self._spazArray9[s].node.moveUpDown = -1
                self._spazArray10[s].node.moveUpDown = -1
                self._spazArray11[s].node.moveUpDown = -1
                self._spazArray12[s].node.moveUpDown = -1
                self._spazArray13[s].node.moveUpDown = -1
                self._spazArray14[s].node.moveUpDown = -1
                self._spazArray15[s].node.moveUpDown = -1
                self._spazArray16[s].node.moveUpDown = -1
                
            def stop():
                s = int(random.random() * len(self._spazArray))
                self._spazArray[s].node.moveUpDown = 0
                self._spazArray0[s].node.moveUpDown = 0
                self._spazArray2[s].node.moveUpDown = 0
                self._spazArray3[s].node.moveUpDown = 0
                self._spazArray4[s].node.moveUpDown = 0
                self._spazArray5[s].node.moveUpDown = 0
                self._spazArray6[s].node.moveUpDown = 0
                self._spazArray7[s].node.moveUpDown = 0
                self._spazArray8[s].node.moveUpDown = 0
                self._spazArray9[s].node.moveUpDown = 0
                self._spazArray10[s].node.moveUpDown = 0
                self._spazArray11[s].node.moveUpDown = 0
                self._spazArray12[s].node.moveUpDown = 0
                self._spazArray13[s].node.moveUpDown = 0
                self._spazArray14[s].node.moveUpDown = 0
                self._spazArray15[s].node.moveUpDown = 0
                self._spazArray16[s].node.moveUpDown = 0
                
            def stopTime():
                bs.getSharedObject('globals').paused = True
                             
            bs.gameTimer(50, bs.Call(position),repeat = False)
            bs.gameTimer(300, bs.Call(stop),repeat = False)
            bs.gameTimer(1850, bs.Call(stopTime),repeat = False)
                
        elif settings.event == 'event_3':
            bsGlobals.ambientColor = (0.8, 1.3, 0.8)
            bsGlobals.vignetteOuter = (0.8, 0.8, 0.8)
            bsGlobals.vignetteInner = (1, 1, 1)
            bsGlobals.cameraMode = 'follow'
            tint = (0.75, 0.75, 0.75)
            self.color = (1, 1, 1)
            
            # play standart music
            #bs.playMusic('Menu')
            
###################################
            self._spazArray = []

            if bs.getEnvironment()['platform'] != 'android':
                count = 30
            else:
                count = 15

            for i in range(count):
                s = bs.Spaz(color=(random.random(), random.random(),
                                   random.random()))

                s.node.handleMessage(
                    bs.StandMessage(
                        position=(random.randint(-4, 4),
                                  3,
                                  random.randint(-7, 1)),
                        angle=int(random.random()*360)))

                s.node.handleMessage('celebrate', 5430000)
                self._spazArray.append(s)
			
            def msg_spaz():
                s = int(random.random() * len(self._spazArray))
                bs.Spaz(character = random.choice(['B-9000','Bernard','Bones','Pascal','Pixel']),color = (random.random(),random.random(),random.random()),highlight = (random.random(),random.random(),random.random())).autoRetain().node.handleMessage(bs.StandMessage(position = (0,6,-4)))
                self._spazArray[s].node.handleMessage(bs.EspectralMessage())
                if not s == 15:
                    bs.gameTimer(50, bs.Call(jump))


            bs.gameTimer(10000, bs.Call(msg_spaz),repeat = True)
            
            
###################################
            self._spazArray1 = []

            if bs.getEnvironment()['platform'] != 'android':
                count = 1
            else:
                count = 1

            for i in range(count):
                s = bs.Spaz(color=(random.random(), random.random(),
                                   random.random()))

                s.node.handleMessage(
                    bs.StandMessage(
                        position=(-7,
                                  5,
                                  1),
                        angle=int(random.random()*360)))

                s.node.handleMessage('celebrate', 5430000)
                s.bombType = 'magicBomb'
                self._spazArray1.append(s)
			
            def stop():
                s = int(random.random() * len(self._spazArray1))
                self._spazArray1[s].node.moveUpDown = 0
                self._spazArray1[s].node.moveLeftRight = 0
                    
            def move():
                s = int(random.random() * len(self._spazArray1))
                self._spazArray1[s].node.moveUpDown = 1
        
            def move2():
                s = int(random.random() * len(self._spazArray1))
                self._spazArray1[s].node.moveLeftRight = 1
        
            def move3():
                s = int(random.random() * len(self._spazArray1))
                self._spazArray1[s].node.moveUpDown = -1
                            
            def move4():
                s = int(random.random() * len(self._spazArray1))
                self._spazArray1[s].node.moveLeftRight = -1
           
            def bomb():
                s = int(random.random() * len(self._spazArray1))
                self._spazArray1[s].onBombPress()
                self._spazArray1[s].onBombRelease()
        
            def punch():
                s = int(random.random() * len(self._spazArray1))
                self._spazArray1[s].onPunchRelease()
                self._spazArray1[s].onPunchRelease()


            bs.gameTimer(1000, bs.Call(move))
            bs.gameTimer(2000, bs.Call(stop))
            bs.gameTimer(2000, bs.Call(move2))
            bs.gameTimer(4000, bs.Call(stop))
            bs.gameTimer(4000, bs.Call(move))
            bs.gameTimer(5000, bs.Call(stop))
            bs.gameTimer(5000, bs.Call(move2))
            bs.gameTimer(6000, bs.Call(stop))
            bs.gameTimer(6000, bs.Call(move))
            bs.gameTimer(7000, bs.Call(stop))
            bs.gameTimer(7000, bs.Call(move3))
            bs.gameTimer(10000, bs.Call(stop))
            bs.gameTimer(11000, bs.Call(bomb))
            
###################################
            self._spazArray2 = []

            if bs.getEnvironment()['platform'] != 'android':
                count = 1
            else:
                count = 1

            for i in range(count):
                s = bs.Spaz(color=(random.random(), random.random(),
                                   random.random()),character='Kronk')

                s.node.handleMessage(
                    bs.StandMessage(
                        position=(7,
                                  5,
                                  1),
                        angle=int(random.random()*360)))

                s._punchPowerScale = 10
                s.hitPoints = 1
               
                self._spazArray2.append(s)
			
            def stop():
                s = int(random.random() * len(self._spazArray2))
                self._spazArray2[s].node.moveUpDown = 0
                self._spazArray2[s].node.moveLeftRight = 0
                    
            def move():
                s = int(random.random() * len(self._spazArray2))
                self._spazArray2[s].node.moveUpDown = 1

        
            def move2():
                s = int(random.random() * len(self._spazArray2))
                self._spazArray2[s].node.moveLeftRight = 1
        
            def move3():
                s = int(random.random() * len(self._spazArray2))
                self._spazArray2[s].node.moveUpDown = -1
                            
            def move4():
                s = int(random.random() * len(self._spazArray2))
                self._spazArray2[s].node.moveLeftRight = -1
                    
            def run():
                s = int(random.random() * len(self._spazArray2))
                self._spazArray2[s].node.run = 1
                
            def bomb():
                s = int(random.random() * len(self._spazArray2))
                self._spazArray2[s].onBombPress()
                self._spazArray2[s].onBombRelease()
        
            def punch():
                s = int(random.random() * len(self._spazArray2))
                self._spazArray2[s].onPunchPress()
                self._spazArray2[s].onPunchRelease()
                    
            def jump():
                s = int(random.random() * len(self._spazArray2))
                self._spazArray2[s].onJumpPress()
                self._spazArray2[s].onJumpRelease()

            bs.gameTimer(5000, bs.Call(jump))
            bs.gameTimer(8000, bs.Call(move4))
            bs.gameTimer(8150, bs.Call(stop))
            bs.gameTimer(11000, bs.Call(punch))
           
###################################
            def spawnCCube():
                pos = (0, 4, -4)
                if not random.random() > 0.9997:
                    cC = bs.Powerup(
                        position=pos,
                        powerupType=('health')).autoRetain()

                    cC.node.extraAcceleration = (0, 0, 0)
                    cC.node.velocity = (random.random(),
                                        random.random()*3,
                                        random.random())

            bs.gameTimer(3000, bs.Call(spawnCCube), repeat=False)
            #bs.gameTimer(3500, bs.Call(spawnCCube), repeat=False)


        elif settings.event == 'event_4':
            bsGlobals.ambientColor = (0.8, 1.3, 0.8)
            bsGlobals.vignetteOuter = (0.8, 0.8, 0.8)
            bsGlobals.vignetteInner = (1, 1, 1)
            bsGlobals.cameraMode = 'follow'
            tint = (0.75, 0.75, 0.75)
            self.color = (1, 1, 1)
###################################
            self._spazArray1 = []

            if bs.getEnvironment()['platform'] != 'android':
                count = 1
            else:
                count = 1

            for i in range(count):
                s = bs.Spaz(color=(random.random(), random.random(),
                                   random.random()))

                s.node.handleMessage(
                    bs.StandMessage(
                        position=(-7,
                                  5,
                                  1),
                        angle=int(random.random()*360)))

                s.node.handleMessage('celebrate', 5430000)
                s.bombType = 'magicBomb'
                self._spazArray1.append(s)
			
            def stop():
                s = int(random.random() * len(self._spazArray1))
                self._spazArray1[s].node.moveUpDown = 0
                self._spazArray1[s].node.moveLeftRight = 0
                    
            def move():
                s = int(random.random() * len(self._spazArray1))
                self._spazArray1[s].node.moveUpDown = 1
        
            def move2():
                s = int(random.random() * len(self._spazArray1))
                self._spazArray1[s].node.moveLeftRight = 1
        
            def move3():
                s = int(random.random() * len(self._spazArray1))
                self._spazArray1[s].node.moveUpDown = -1
                            
            def move4():
                s = int(random.random() * len(self._spazArray1))
                self._spazArray1[s].node.moveLeftRight = -1
           
            def bomb():
                s = int(random.random() * len(self._spazArray1))
                self._spazArray1[s].onBombPress()
                self._spazArray1[s].onBombRelease()
        
            def punch():
                s = int(random.random() * len(self._spazArray1))
                self._spazArray1[s].onPunchRelease()
                self._spazArray1[s].onPunchRelease()


            bs.gameTimer(1000, bs.Call(move))
            bs.gameTimer(2000, bs.Call(stop))
            bs.gameTimer(2000, bs.Call(move2))
            bs.gameTimer(4000, bs.Call(stop))
            bs.gameTimer(4000, bs.Call(move))
            bs.gameTimer(5000, bs.Call(stop))
            bs.gameTimer(5000, bs.Call(move2))
            bs.gameTimer(6000, bs.Call(stop))
            bs.gameTimer(6000, bs.Call(move))
            bs.gameTimer(7000, bs.Call(stop))
            bs.gameTimer(7000, bs.Call(move3))
            bs.gameTimer(10000, bs.Call(stop))
            #bs.gameTimer(11000, bs.Call(bomb))
            
            # play standart music
            bs.playMusic('Menu')

            def spawnCCube():
                pos = (0,5.5,-3)
                if not random.random() > 0.9997:
                    cC = Box(position=pos,texture='powerupCurse')

                    cC.node.extraAcceleration = (0, 0, 0)
                    #cC.node.velocity = (random.random()*-10,
                                        #random.random()*3,
                                       # random.random()*3)

            bs.gameTimer(50, bs.Call(spawnCCube), repeat=False)
            
            
        elif settings.event == 'event_5':
            bsGlobals.ambientColor = (0.1, 0.6, 1)
            bsGlobals.vignetteOuter = (0.45, 0.55, 0.54)
            bsGlobals.vignetteInner = (0.99, 0.98, 0.98)
            tint = (0.78, 0.78, 0.82)
            self.color = (0.92, 0.91, 0.93)
            
            self.bg = bs.NodeActor(bs.newNode('terrain', attrs={
                'model': bgModel,
                'color': self.color,
                'lighting': False,
                'background': True,
                'colorTexture': bgTex2}))

            def dropB():
                pos = (0,4,-15)
                vel = (0,0,0)

                bs.Bomb(
                    position=pos,
                    velocity=vel,
                    bombType='menu',
                    blastRadius=0).autoRetain().node.extraAcceleration = (0,20,3) 

                bs.gameTimer(1000, dropB)
                bs.gameTimer(1200, dropB1)
                bs.gameTimer(1400, dropB2)
                bs.gameTimer(1600, dropB3)
                bs.gameTimer(1800, dropB4)
                bs.gameTimer(2000, dropB5)
                bs.gameTimer(2200, dropB6)
                bs.gameTimer(2400, dropB7)
                
            def dropB1():
                pos = (0,5,15)
                vel = (0,0,0)

                bs.Bomb(
                    position=pos,
                    velocity=vel,
                    bombType='menu',
                    blastRadius=0).autoRetain().node.extraAcceleration = (0,20,-3) 
                                    
            def dropB2():
                pos = (-15,6,0)
                vel = (0,0,0)

                bs.Bomb(
                    position=pos,
                    velocity=vel,
                    bombType='menu',
                    blastRadius=0).autoRetain().node.extraAcceleration = (3,20,0) 
                                    
            def dropB3():
                pos = (15,7,0)
                vel = (0,0,0)

                bs.Bomb(
                    position=pos,
                    velocity=vel,
                    bombType='menu',
                    blastRadius=0).autoRetain().node.extraAcceleration = (-3,20,0) 
                                    
            def dropB4():
                pos = (-15,8,-15)
                vel = (0,0,0)

                bs.Bomb(
                    position=pos,
                    velocity=vel,
                    bombType='menu',
                    blastRadius=0).autoRetain().node.extraAcceleration = (3,20,3) 
                                    
            def dropB5():
                pos = (15,9,15)
                vel = (0,0,0)

                bs.Bomb(
                    position=pos,
                    velocity=vel,
                    bombType='menu',
                    blastRadius=0).autoRetain().node.extraAcceleration = (-3,20,-3) 
                                    
            def dropB6():
                pos = (-15,10,15)
                vel = (0,0,0)

                bs.Bomb(
                    position=pos,
                    velocity=vel,
                    bombType='menu',
                    blastRadius=0).autoRetain().node.extraAcceleration = (3,20,-3) 
                                    
            def dropB7():
                pos = (15,11,-15)
                vel = (0,0,0)

                bs.Bomb(
                    position=pos,
                    velocity=vel,
                    bombType='menu',
                    blastRadius=0).autoRetain().node.extraAcceleration = (-3,20,3) 

            dropB()
            
        elif settings.event == 'event_6':
            bsGlobals.ambientColor = (1, 1, 1) #(0.1, 0.6, 1)
            bsGlobals.vignetteOuter = (0.45, 0.55, 0.54)
            bsGlobals.vignetteInner = (0.99, 0.98, 0.98)
            tint = (0.78, 0.78, 0.82)
            self.color = (0.92, 0.91, 0.93)

            def dropB():
                pos = (-15 + random.random()*30, 15, -15 + random.random()*30)

                velB1 = (-5.0 + random.random()*30.0) \
                    * (-1.0 if pos[0] > 0 else 1.0)

                vel = (velB1, -4.0, 0)

                bs.Bomb(
                    position=pos,
                    velocity=vel,
                    bombType='normal').autoRetain()

                bs.gameTimer(random.randint(50, 200), dropB)

            dropB()
            
####################################
        random.seed()
        

            
        # on the main menu, also show our news..
        class News(object):
            
            def __init__(self,activity):
                self._valid = True
                self._messageDuration = 10000
                self._messageSpacing = 2000
                self._text = None
                self._activity = weakref.ref(activity)
                # if we're signed in, fetch news immediately..
                # otherwise wait until we are signed in
                self._fetchTimer = bs.Timer(1000,
                                            bs.WeakCall(self._tryFetchingNews),
                                            repeat=True)
                self._tryFetchingNews()

            # we now want to wait until we're signed in before fetching news
            def _tryFetchingNews(self):
                if bsInternal._getAccountState() == 'SIGNED_IN':
                    self._fetchNews()
                    self._fetchTimer = None
                
            def _fetchNews(self):
                try: launchCount = bs.getConfig()['launchCount']
                except Exception: launchCount = None
                global gLastNewsFetchTime
                gLastNewsFetchTime = time.time()
                
                # UPDATE - we now just pull news from MRVs
                news = bsInternal._getAccountMiscReadVal('n', None)
                if news is not None:
                    self._gotNews(news)

            def _changePhrase(self):

                global gLastNewsFetchTime
                
                # if our news is way out of date, lets re-request it..
                # otherwise, rotate our phrase
                if time.time()-gLastNewsFetchTime > 600.0:
                    self._fetchNews()
                    self._text = None
                else:
                    if self._text is not None:
                        if len(self._phrases) == 0:
                            for p in self._usedPhrases:
                                self._phrases.insert(0,p)
                        val = self._phrases.pop()
                        if val == '__ACH__':
                            vr = bs.getEnvironment()['vrMode']
                            bsUtils.Text(
                                bs.Lstr(resource='nextAchievementsText'),
                                color=(0,1,1,1) if vr else (0.95,0.9,1,0.4),
                                hostOnly=True,
                                maxWidth=200,
                                position=(-300, -35),
                                hAlign='right',
                                transition='fadeIn',
                                scale=0.9 if vr else 0.7,
                                flatness=1.0 if vr else 0.6,
                                shadow=1.0 if vr else 0.5,
                                hAttach="center",
                                vAttach="top",
                                transitionDelay=1000,
                                transitionOutDelay=self._messageDuration)\
                                   .autoRetain()
                            import bsAchievement
                            achs = [a for a in bsAchievement.gAchievements
                                    if not a.isComplete()]
                            if len(achs) > 0:
                                a = achs.pop(random.randrange(min(4,len(achs))))
                                a.createDisplay(-180, -35, 1000,
                                                outDelay=self._messageDuration,
                                                style='news')
                            if len(achs) > 0:
                                a = achs.pop(random.randrange(min(8,len(achs))))
                                a.createDisplay(180, -35, 1250,
                                                outDelay=self._messageDuration,
                                                style='news')
                        else:
                            s = self._messageSpacing
                            keys = {s:0, s+1000:1.0,
                                    s+self._messageDuration-1000:1.0,
                                    s+self._messageDuration:0.0}
                            bs.animate(self._text.node, "opacity",
                                       dict([[k,v] for k,v in keys.items()]))
                            self._text.node.text = val

            def _gotNews(self, news):
                
                # run this stuff in the context of our activity since we need
                # to make nodes and stuff.. should fix the serverGet call so it 
                activity = self._activity()
                if activity is None or activity.isFinalized(): return
                with bs.Context(activity):
                
                    self._phrases = []
                    # show upcoming achievements in non-vr versions
                    # (currently too hard to read in vr)
                    self._usedPhrases = (
                        ['__ACH__'] if not bs.getEnvironment()['vrMode']
                        else []) + [s for s in news.split('<br>\n') if s != '']
                    self._phraseChangeTimer = bs.Timer(
                        self._messageDuration+self._messageSpacing,
                        bs.WeakCall(self._changePhrase), repeat=True)

                    sc = 1.2 if (bs.getEnvironment()['interfaceType'] == 'small'
                                 or bs.getEnvironment()['vrMode']) else 0.8

                    self._text = bs.NodeActor(bs.newNode('text', attrs={
                        'vAttach':'top',
                        'hAttach':'center',
                        'hAlign':'center',
                        'vrDepth':-20,
                        'shadow':1.0 if bs.getEnvironment()['vrMode'] else 0.4,
                        'flatness':0.8,
                        'vAlign':'top',
                        'color':((0, 1, 1, 1) if bs.getEnvironment()['vrMode']
                                 else (0.7, 0.65, 0.75, 1.0)),
                        'scale':sc,
                        'maxWidth':900.0/sc,
                        'position':(0,-10)}))
                    self._changePhrase()
                    
        if not env['kioskMode'] and not env.get('toolbarTest', True):
            self._news = News(self)

        # bring up the last place we were, or start at the main menu otherwise
        with bs.Context('UI'):
            try: mainWindow = bsUI.gMainWindow
            except Exception: mainWindow = None

            # when coming back from a kiosk-mode game, jump to
            # the kiosk start screen.. if bsUtils.gRunningKioskModeGame:
            if bs.getEnvironment()['kioskMode']:
                bsUI.uiGlobals['mainMenuWindow'] = \
                     bsUI.KioskWindow().getRootWidget()
            # ..or in normal cases go back to the main menu
            else:
                if mainWindow == 'Gather':
                    bsUI.uiGlobals['mainMenuWindow'] = \
                        bsUI.GatherWindow(transition=None).getRootWidget()
                elif mainWindow == 'Watch':
                    bsUI.uiGlobals['mainMenuWindow'] = \
                        bsUI.WatchWindow(transition=None).getRootWidget()
                elif mainWindow == 'Team Game Select':
                    bsUI.uiGlobals['mainMenuWindow'] = \
                        bsUI.TeamsWindow(sessionType=bs.TeamsSession,
                                         transition=None).getRootWidget()
                elif mainWindow == 'Free-for-All Game Select':
                    bsUI.uiGlobals['mainMenuWindow'] = \
                        bsUI.TeamsWindow(sessionType=bs.FreeForAllSession,
                                         transition=None).getRootWidget()
                elif mainWindow == 'Coop Select':
                    bsUI.uiGlobals['mainMenuWindow'] = \
                        bsUI.CoopWindow(transition=None).getRootWidget()
                else: bsUI.uiGlobals['mainMenuWindow'] = \
                    bsUI.MainMenuWindow(transition=None).getRootWidget()

                # attempt to show any pending offers immediately.
                # If that doesn't work, try again in a few seconds
                # (we may not have heard back from the server)
                # ..if that doesn't work they'll just have to wait
                # until the next opportunity.
                if not bsUI._showOffer():
                    def tryAgain():
                        if not bsUI._showOffer():
                            # try one last time..
                            bs.realTimer(2000, bsUI._showOffer)
                    bs.realTimer(2000, tryAgain)
            
        gDidInitialTransition = True
        
    def _cameraFlash(self,duration=999):
        xSpread = 15
        ySpread = 10
        positions = [[-xSpread,-ySpread],[0,-ySpread],[0,ySpread],[xSpread,-ySpread],[xSpread,ySpread],[-xSpread,ySpread]]
        times = [0,2700,1000,1800,500,1400]

        self._cameraFlash = []
        for i in range(6):
            light = bs.NodeActor(bs.newNode("light",
                                            attrs={'position':(positions[i][0],0,positions[i][1]),
                                                   'radius':1.0,
                                                   'lightVolumes':False,
                                                   'heightAttenuated':False,
                                                   'color':(random.random(),random.random(),random.random())}))
            s = 1.87
            iScale = 1.3
            tcombine = bs.newNode("combine",owner=light.node,attrs={'size':3,'input0':positions[i][0],'input1':0,'input2':positions[i][1]})
            tcombine.connectAttr('output',light.node,'position')
            x = positions[i][0]
            y = positions[i][1]
            spd = 0.5 + random.random()
            spd2 = 0.5 + random.random()
            bsUtils.animate(tcombine,'input0',{0:x+0, 69*spd:x+10.0, 143*spd:x-10.0, 201*spd:x+0},loop=True)
            bsUtils.animate(tcombine,'input2',{0:y+0, 150*spd2:y+10.0, 287*spd2:y-10.0, 398*spd2:y+0},loop=True)
            
            bsUtils.animate(light.node,"intensity",{0:0, 20*s:0, 50*s:0.8*iScale, 80*s:0, 100*s:0},loop=True,offset=times[i])
            bs.gameTimer(int(times[i]+random.randint(1,duration)*40*s),light.node.delete)
            self._cameraFlash.append(light)
            
    def dropB(self):
        pos = (0,4,-15)
        vel = (0,0,0)
        bs.Bomb(position=pos,velocity=vel,blastRadius=0,bombType = 'menu').autoRetain().node.extraAcceleration = (0,20,3) 
       
    def dropB1(self):
        pos = (0,5,15)
        vel = (0,0,0)
        bs.Bomb(position=pos,velocity=vel,blastRadius=0,bombType = 'menu').autoRetain().node.extraAcceleration = (0,20,-3) 
        
    def dropB2(self):
        pos = (-15,6,0)
        vel = (0,0,0)
        bs.Bomb(position=pos,velocity=vel,blastRadius=0,bombType = 'menu').autoRetain().node.extraAcceleration = (3,20,0) 
        
    def dropB3(self):
        pos = (15,7,0)
        vel = (0,0,0)
        bs.Bomb(position=pos,velocity=vel,blastRadius=0,bombType = 'menu').autoRetain().node.extraAcceleration = (-3,20,0)

    def dropB4(self):
        pos = (-15,8,-15)
        vel = (0,0,0)
        bs.Bomb(position=pos,velocity=vel,blastRadius=0,bombType = 'menu').autoRetain().node.extraAcceleration = (3,20,3) 
        
    def dropB5(self):
        pos = (15,9,15)
        vel = (0,0,0)
        bs.Bomb(position=pos,velocity=vel,blastRadius=0,bombType = 'menu').autoRetain().node.extraAcceleration = (-3,20,-3) 
        
    def dropB6(self):
        pos = (-15,10,15)
        vel = (0,0,0)
        bs.Bomb(position=pos,velocity=vel,blastRadius=0,bombType = 'menu').autoRetain().node.extraAcceleration = (3,20,-3) 
        
    def dropB7(self):
        pos = (15,11,-15)
        vel = (0,0,0)
        bs.Bomb(position=pos,velocity=vel,blastRadius=0,bombType = 'menu').autoRetain().node.extraAcceleration = (-3,20,3)
		
    #def upB(self):
        #pos = (-15+random.random()*30,0,-15+random.random()*30)
        #vel = ((-5.0+random.random()*10.0) * (-1.0 if pos[0] > 0 else 1.0),random.randrange(1,5),0)
        #b = bs.Bomb(position=pos,velocity=vel,bombType = 'cube').autoRetain()
        #b.node.gravityScale = 0
		
    #def spamB(self):
        #pos = (-15+random.random()*30,random.randrange(5,15),-15+random.random()*30)
        #bs.Blast(position=pos,blastRadius = random.randint(2,5)).autoRetain()
		
    #def partyColor(self):
        #bs.getSharedObject('globals').tint = (random.random()*2,random.random()*2,random.random()*2)
                  
    def dropP(self):
        pos = (random.uniform(-10,10),14,random.uniform(-10,10)) #(-18+random.random()*30,-10,-18+random.random()*30)
        vel = (0,-5,0) #((-5.0+random.random()*30.0) * (-1.0 if pos[0] > 0 else 1.0), -4.0,0)
        bs.Powerup(position=pos,powerupType=bs.Powerup.getFactory().getRandomPowerupType()).autoRetain().node.extraAcceleration = (0,18,0) 
        ##pos = (-15+random.random()*30,random.randrange(5,15),-15+random.random()*30)
        ##bs.Blast(position=pos,blastRadius = random.randint(2,5)).autoRetain()
        ###bs.getSharedObject('globals').tint = (random.random()*2,random.random()*2,random.random()*2)

    def _update(self):

        # update logo in case it changes..
        if self._logoNode is not None and self._logoNode.exists():
            customTexture = self._getCustomLogoTexName()
            if customTexture != self._customLogoTexName:
                self._customLogoTexName = customTexture
                self._logoNode.texture = bs.getTexture(
                    customTexture if customTexture is not None else 'logo')
                self._logoNode.modelOpaque = (
                    None if customTexture is not None else bs.getModel('logo'))
                self._logoNode.modelTransparent = (
                    None if customTexture is not None
                    else bs.getModel('logoTransparent'))
        
        # if language has changed, recreate our logo text/graphics
        l = bs.getLanguage()
        if l != self._language:
            self._language = l
            env = bs.getEnvironment()
            y = 20 if bsUI.gSmallUI else 20 if bsUI.gMedUI else 140
            self._wordActors = []
            baseDelay = 1000
            delay = baseDelay
            delayInc = 20
            gScale = 1.1
            
            # come on faster after the first time
            if gDidInitialTransition:
                baseDelay = 0
                delay = baseDelay
                delayInc = 20
                
            # we draw higher in kiosk mode (make sure to test this
            # when making adjustments) for now we're hard-coded for
            # a few languages.. should maybe look into generalizing this?..
            if bs.getLanguage() == 'Chinese':
                baseX = -270
                x = baseX-20
                spacing = 85*gScale
                yExtra = 0 if env['kioskMode'] else 0
                self._makeLogo(x-110+50, 113+y+1.2*yExtra, 0.34*gScale,
                               delay=baseDelay+100,
                               customTexture='chTitleChar1', jitterScale=2.0,
                               vrDepthOffset=-30)
                x += spacing
                delay += delayInc
                self._makeLogo(x-10+50, 110+y+1.2*yExtra, 0.31*gScale,
                               delay=baseDelay+150,
                               customTexture='chTitleChar2',
                               jitterScale=2.0, vrDepthOffset=-30)
                x += 2.0 * spacing
                delay += delayInc
                self._makeLogo(x+180-140, 110+y+1.2*yExtra, 0.3*gScale,
                               delay=baseDelay+250,
                               customTexture='chTitleChar3', jitterScale=2.0,
                               vrDepthOffset=-30)
                x += spacing
                delay += delayInc
                self._makeLogo(x+241-120, 110+y+1.2*yExtra, 0.31*gScale,
                               delay=baseDelay+300,
                               customTexture='chTitleChar4', jitterScale=2.0,
                               vrDepthOffset=-30)
                x += spacing; delay += delayInc
                self._makeLogo(x+300-90, 105+y+1.2*yExtra, 0.34*gScale,
                               delay=baseDelay+350,
                               customTexture='chTitleChar5', jitterScale=2.0,
                               vrDepthOffset=-30)
                self._makeLogo(baseX+155, 146+y+1.2*yExtra, 0.28*gScale,
                               delay=baseDelay+200, rotate=-7)
            else:
                baseX = -170
                x = baseX-20
                spacing = 55*gScale
                yExtra = 0 if env['kioskMode'] else 0

                x1 = x
                delay1 = delay
                for shadow in (True, False):
                    x = x1
                    delay = delay1
                    self._makeWord('C', x-25 if bsUI.gSmallUI else x-50 if bsUI.gMedUI else x-50, y-23+0.8*yExtra if bsUI.gSmallUI else y-23+0.8*yExtra+50 if bsUI.gMedUI else y-43+0.8*yExtra, 
								   scale=1.3*gScale if bsUI.gSmallUI else 1.0*gScale if bsUI.gMedUI else 0.8*gScale,
                                   delay=delay, vrDepthOffset=3, shadow=shadow)
                    x += spacing
                    delay += delayInc
                    self._makeWord('r', x-60 if bsUI.gSmallUI else x-80 if bsUI.gMedUI else x-85, y+yExtra-10 if bsUI.gSmallUI else y-23+0.8*yExtra+60 if bsUI.gMedUI else y-23+0.8*yExtra, delay=delay,
                                   scale=1.1*gScale if bsUI.gSmallUI else 0.9*gScale if bsUI.gMedUI else 0.7*gScale, vrDepthOffset=5,
                                   shadow=shadow)
                    x += spacing*0.2
                    delay += delayInc
                    self._makeWord('a', x-15 if bsUI.gSmallUI else x-40 if bsUI.gMedUI else x-44, y+yExtra-10 if bsUI.gSmallUI else y-23+0.8*yExtra+60 if bsUI.gMedUI else y-23+0.8*yExtra, delay=delay,
                                   scale=1.1*gScale if bsUI.gSmallUI else 0.9*gScale if bsUI.gMedUI else 0.7*gScale, vrDepthOffset=5,
                                   shadow=shadow)
                    x += spacing*0.8
                    delay += delayInc
                    self._makeWord('z', x-15 if bsUI.gSmallUI else x-40 if bsUI.gMedUI else x-38, y+yExtra-10 if bsUI.gSmallUI else y-23+0.8*yExtra+60 if bsUI.gMedUI else y-23+0.8*yExtra, delay=delay,
                                   scale=1.1*gScale if bsUI.gSmallUI else 0.9*gScale if bsUI.gMedUI else 0.7*gScale, vrDepthOffset=5,
                                   shadow=shadow)
                    x += spacing*0.8
                    delay += delayInc
                    self._makeWord('y', x-20 if bsUI.gSmallUI else x-50 if bsUI.gMedUI else x-46, y+yExtra-10 if bsUI.gSmallUI else y-23+0.8*yExtra+60 if bsUI.gMedUI else y-23+0.8*yExtra, delay=delay,
                                   scale=1.1*gScale if bsUI.gSmallUI else 0.9*gScale if bsUI.gMedUI else 0.7*gScale, vrDepthOffset=5,
                                   shadow=shadow)
                    x += spacing*0.85
                    delay += delayInc
                    self._makeWord('S', x-10 if bsUI.gSmallUI else x-40 if bsUI.gMedUI else x-34, y-25+0.8*yExtra if bsUI.gSmallUI else y-23+0.8*yExtra+50 if bsUI.gMedUI else y-43+0.8*yExtra, 
								   scale=1.35*gScale if bsUI.gSmallUI else 1.0*gScale if bsUI.gMedUI else 0.8*gScale,
                                   delay=delay, vrDepthOffset=14, shadow=shadow)
                    x += spacing
                    delay += delayInc
                    self._makeWord('q', x if bsUI.gSmallUI else x-50 if bsUI.gMedUI else x-45, y+yExtra if bsUI.gSmallUI else y-23+0.8*yExtra+60 if bsUI.gMedUI else y-23+0.8*yExtra, 
								   delay=delay, scale=gScale if bsUI.gSmallUI else 0.9*gScale if bsUI.gMedUI else 0.7*gScale,
                                   shadow=shadow)
                    x += spacing*0.9
                    delay += delayInc
                    self._makeWord('u', x if bsUI.gSmallUI else x-50 if bsUI.gMedUI else x-43, y+yExtra if bsUI.gSmallUI else y-23+0.8*yExtra+60 if bsUI.gMedUI else y-23+0.8*yExtra, 
								   delay=delay, scale=gScale if bsUI.gSmallUI else 0.9*gScale if bsUI.gMedUI else 0.7*gScale,
                                   vrDepthOffset=7, shadow=shadow)
                    x += spacing*0.9
                    delay += delayInc
                    self._makeWord('a', x if bsUI.gSmallUI else x-50 if bsUI.gMedUI else x-43, y+yExtra if bsUI.gSmallUI else y-23+0.8*yExtra+60 if bsUI.gMedUI else y-23+0.8*yExtra, 
								   delay=delay, scale=gScale if bsUI.gSmallUI else 0.9*gScale if bsUI.gMedUI else 0.7*gScale,
                                   shadow=shadow)
                    x += spacing*0.64
                    delay += delayInc
                    self._makeWord('d', x if bsUI.gSmallUI else x-30 if bsUI.gMedUI else x-25, y+yExtra-10 if bsUI.gSmallUI else y-23+0.8*yExtra+60 if bsUI.gMedUI else y-23+0.8*yExtra, delay=delay,
                                   scale=1.1*gScale if bsUI.gSmallUI else 0.9*gScale if bsUI.gMedUI else 0.7*gScale, vrDepthOffset=6,
                                   shadow=shadow)
                    self._makeWord2('M', x-10 if bsUI.gSmallUI else x-50 if bsUI.gMedUI else x-25, y-125+0.7*yExtra if bsUI.gSmallUI else y+0.7*yExtra if bsUI.gMedUI else y-125+0.7*yExtra, scale=0.36*gScale,
                                   delay=delay, vrDepthOffset=14, shadow=shadow)
                    x += spacing
                    delay += delayInc
                    self._makeWord2('o', x+3 if bsUI.gSmallUI else x-40 if bsUI.gMedUI else x-25, y-125+0.7*yExtra if bsUI.gSmallUI else y+0.7*yExtra if bsUI.gMedUI else y-125+0.7*yExtra, delay=delay, scale=0.35*gScale,
                                   shadow=shadow)
                    x += spacing*0.9
                    delay += delayInc
                    self._makeWord2('d', x if bsUI.gSmallUI else x-40 if bsUI.gMedUI else x-25, y-125+0.7*yExtra if bsUI.gSmallUI else y+0.7*yExtra if bsUI.gMedUI else y-125+0.7*yExtra, delay=delay, scale=0.35*gScale,
                                   vrDepthOffset=7, shadow=shadow)
                    x += spacing*0.9
                    delay += delayInc
                    self._makeWord2('P', x if bsUI.gSmallUI else x-40 if bsUI.gMedUI else x-25, y-125+0.7*yExtra if bsUI.gSmallUI else y+0.7*yExtra if bsUI.gMedUI else y-125+0.7*yExtra, delay=delay, scale=0.36*gScale,
                                   shadow=shadow)
                    x += spacing*0.9
                    delay += delayInc
                    self._makeWord2('a', x if bsUI.gSmallUI else x-40 if bsUI.gMedUI else x-25, y-125+0.7*yExtra if bsUI.gSmallUI else y+0.7*yExtra if bsUI.gMedUI else y-125+0.7*yExtra, delay=delay, scale=0.35*gScale,
                                   vrDepthOffset=7, shadow=shadow)
                    x += spacing*0.9
                    delay += delayInc
                    self._makeWord2('c', x if bsUI.gSmallUI else x-40 if bsUI.gMedUI else x-25, y-125+0.7*yExtra if bsUI.gSmallUI else y+0.7*yExtra if bsUI.gMedUI else y-125+0.7*yExtra, delay=delay, scale=0.35*gScale,
                                   shadow=shadow)
                    x += spacing*0.9
                    delay += delayInc
                    self._makeWord2('k', x if bsUI.gSmallUI else x-40 if bsUI.gMedUI else x-25, y-125+0.7*yExtra if bsUI.gSmallUI else y+0.7*yExtra if bsUI.gMedUI else y-125+0.7*yExtra, delay=delay, scale=0.35*gScale,
                                   vrDepthOffset=7, shadow=shadow)
                    x += spacing*0.9
                    delay += delayInc
                self._makeLogo(baseX+450 if bsUI.gSmallUI else baseX+420 if bsUI.gMedUI else baseX+450, y+1.0*yExtra  if bsUI.gSmallUI else y+55+1.0*yExtra if bsUI.gMedUI else y+1.0*yExtra, 0.08*gScale,
                               delay=baseDelay)
                self._crazyLogo(baseX-465, 0+y+330+1.0*yExtra, 0.04*gScale if settings.theme == 'themeCSMP' else 0,
                               delay=baseDelay+200)
                self._crazyLogo(baseX-465, 0+y+305+1.0*yExtra, 0.04*gScale if settings.theme == 'themeCSMP' else 0,
                               delay=baseDelay)
                self._crazyLogo(baseX-440, 0+y+330+1.0*yExtra, 0.04*gScale if settings.theme == 'themeCSMP' else 0,
                               delay=baseDelay+400)
                self._crazyLogo(baseX+800, 0+y+330+1.0*yExtra, 0.04*gScale if settings.theme == 'themeCSMP' else 0,
                               delay=baseDelay+800)
                self._crazyLogo(baseX+800, 0+y+305+1.0*yExtra, 0.04*gScale if settings.theme == 'themeCSMP' else 0,
                               delay=baseDelay+1000)
                self._crazyLogo(baseX+775, 0+y+330+1.0*yExtra, 0.04*gScale if settings.theme == 'themeCSMP' else 0,
                               delay=baseDelay+600)

    def _makeWord(self, word, x, y, scale=1.0, delay=0,
                  vrDepthOffset=0, shadow=False):
        if shadow:
            wordShadowObj = bs.NodeActor(bs.newNode('text', attrs={
                'position':(x,y),
                'big':True,
                'color':(0,0.5,0.5) if settings.theme == 'themeCSMP' else (0.5,0.5,0.5),
                'tiltTranslate':0.09,
                'opacityScalesShadow':False,
                'shadow':0.4,
                'vrDepth':-130,
                'vAlign':'center',
                'projectScale':0.97*scale,
                'scale':0.91,
                'text':word}))
            self._wordActors.append(wordShadowObj)
        else:
            wordObj = bs.NodeActor(bs.newNode('text', attrs={
                'position':(x,y),
                'big':True,
                'color':random.choice([(0,1,1),(0,0.9,1),(0,0.8,1),(0,0.7,1),(0,0.6,1),(0,0.5,1)]) if settings.theme == 'themeCSMP' else (1,1,1), #(0,1.2,1.2,1.0)
                'tiltTranslate':0.11,
                'shadow':0.2,
                'vrDepth':-40+vrDepthOffset,
                'vAlign':'center',
                'projectScale':scale,
                'scale':1.0,
                'text':word}))
            self._wordActors.append(wordObj)
            
            
    def _makeWord2(self, word, x, y, scale=1.0, delay=0,
                  vrDepthOffset=0, shadow=False):
        if shadow:
            wordShadowObj = bs.NodeActor(bs.newNode('text', attrs={
                'position':(x,y),
                'big':True,
                'color':(0,0.5,0.5),
                'tiltTranslate':0.09,
                'opacityScalesShadow':False,
                'shadow':0.4,
                'vrDepth':-130,
                'vAlign':'center',
                'projectScale':0.97*scale,
                'scale':0.91,
                'text':word}))
            self._wordActors.append(wordShadowObj)
        else:
            wordObj = bs.NodeActor(bs.newNode('text', attrs={
                'position':(x,y),
                'big':True,
                'color':gMenuTitleColor2,
                'tiltTranslate':0.11,
                'shadow':0.2,
                'vrDepth':-40+vrDepthOffset,
                'vAlign':'center',
                'projectScale':scale,
                'scale':1.0,
                'text':word}))
            self._wordActors.append(wordObj)

        # add a bit of stop-motion-y jitter to the logo
        # (unless we're in VR mode in which case its best to leave things still)
        if not bs.getEnvironment()['vrMode']:
            if not shadow:
                c = bs.newNode("combine", owner=wordObj.node, attrs={'size':2})
            else:
                c = None
            if shadow:
                c2 = bs.newNode("combine", owner=wordShadowObj.node,
                                attrs={'size':2})
            else:
                c2 = None
            if not shadow:
                c.connectAttr('output',wordObj.node,'position')
            if shadow:
                c2.connectAttr('output',wordShadowObj.node,'position')
            keys = {}
            keys2 = {}
            timeV = 0
            for i in range(10):
                val = x+(random.random()-0.5)*0.8
                val2 = x+(random.random()-0.5)*0.8
                keys[timeV*self._ts] = val
                keys2[timeV*self._ts] = val2+5
                timeV += random.random() * 100
            if c is not None:
                bs.animate(c, "input0", keys, loop=True)
            if c2 is not None:
                bs.animate(c2, "input0", keys2, loop=True)
            keys = {}
            keys2 = {}
            timeV = 0
            for i in range(10):
                val = y+(random.random()-0.5)*0.8
                val2 = y+(random.random()-0.5)*0.8
                keys[timeV*self._ts] = val
                keys2[timeV*self._ts] = val2-9
                timeV += random.random() * 100
            if c is not None: bs.animate(c,"input1",keys,loop=True)
            if c2 is not None: bs.animate(c2,"input1",keys2,loop=True)

        if not shadow:
            bs.animate(wordObj.node, "projectScale",
                       {delay:0.0, delay+100:scale*1.1, delay+200:scale})
        else:
            bs.animate(wordShadowObj.node, "projectScale",
                       {delay:0.0, delay+100:scale*1.1, delay+200:scale})
    def _getCustomLogoTexName(self):
        if bsInternal._getAccountMiscReadVal('easter',False):
            return 'logoEaster'
        else:
            return None
                
        
    # pop the logo and menu in
    def _makeLogo(self, x, y, scale, delay, customTexture=None, jitterScale=1.0,
                  rotate=0, vrDepthOffset=0):
        # temp easter googness
        if customTexture is None:
            customTexture = self._getCustomLogoTexName()
        self._customLogoTexName = customTexture
        logo = bs.NodeActor(bs.newNode('image', attrs={
            'texture': bs.getTexture(customTexture if customTexture is not None
                                     else 'logo'),
            'modelOpaque':(None if customTexture is not None
                           else bs.getModel('logo')),
            'modelTransparent':(None if customTexture is not None
                                else bs.getModel('logoTransparent')),
            'vrDepth':-10+vrDepthOffset,
            'rotate':rotate,
            'attach':"center",
            'tiltTranslate':0.21,
            'absoluteScale':True}))
        self._logoNode = logo.node
        self._wordActors.append(logo)
        # add a bit of stop-motion-y jitter to the logo
        # (unless we're in VR mode in which case its best to leave things still)
        if not bs.getEnvironment()['vrMode']:
            c = bs.newNode("combine", owner=logo.node, attrs={'size':2})
            c.connectAttr('output', logo.node, 'position')
            keys = {}
            timeV = 0
            # gen some random keys for that stop-motion-y look
            for i in range(10):
                keys[timeV] = x+(random.random()-0.5)*0.7*jitterScale
                timeV += random.random() * 100
            bs.animate(c,"input0",keys,loop=True)
            keys = {}
            timeV = 0
            for i in range(10):
                keys[timeV*self._ts] = y+(random.random()-0.5)*0.7*jitterScale
                timeV += random.random() * 100
            bs.animate(c,"input1",keys,loop=True)
        else:
            logo.node.position = (x,y)

        c = bs.newNode("combine",owner=logo.node,attrs={"size":2})

        keys = {delay:0,delay+100:700*scale,delay+200:600*scale}
        bs.animate(c,"input0",keys)
        bs.animate(c,"input1",keys)
        c.connectAttr("output",logo.node,"scale")
        
        
    def _crazyLogo(self, x, y, scale, delay, customTexture=None, jitterScale=1.0,
                  rotate=0, vrDepthOffset=0):
        # temp easter googness
        if customTexture is None:
            customTexture = self._getCustomLogoTexName()
        self._customLogoTexName = customTexture
        logo = bs.NodeActor(bs.newNode('image', attrs={
            'texture': bs.getTexture(customTexture if customTexture is not None
                                     else 'buttonSquare'), #googlePlayLeaderboardsIcon
            'modelOpaque':None,
            'modelTransparent':None,
            'vrDepth':-10+vrDepthOffset,
            'rotate':rotate,
            'attach':"center",
            'tiltTranslate':0.21,
            'color':gMenuTitleColor,
            'absoluteScale':True}))
        self._logoNode = logo.node
        self._wordActors.append(logo)
        # add a bit of stop-motion-y jitter to the logo
        # (unless we're in VR mode in which case its best to leave things still)
        if not bs.getEnvironment()['vrMode']:
            c = bs.newNode("combine", owner=logo.node, attrs={'size':2})
            c.connectAttr('output', logo.node, 'position')
            keys = {}
            timeV = 0
            # gen some random keys for that stop-motion-y look
            for i in range(10):
                keys[timeV] = x+(random.random()-0.5)*0.7*jitterScale
                timeV += random.random() * 100
            bs.animate(c,"input0",keys,loop=True)
            keys = {}
            timeV = 0
            for i in range(10):
                keys[timeV*self._ts] = y+(random.random()-0.5)*0.7*jitterScale
                timeV += random.random() * 100
            bs.animate(c,"input1",keys,loop=True)
        else:
            logo.node.position = (x,y)

        c = bs.newNode("combine",owner=logo.node,attrs={"size":2})

        keys = {delay:0,delay+100:700*scale,delay+200:600*scale}
        bs.animate(c,"input0",keys)
        bs.animate(c,"input1",keys)
        c.connectAttr("output",logo.node,"scale")
            
    def _startPreloads(self):
        # FIXME - the func that calls us back doesn't save/restore state
        # or check for a dead activity so we have to do that ourself..
        if self.isFinalized(): return
        with bs.Context(self): _preload1()

        bs.gameTimer(500,lambda: bs.playMusic('Menu'))
        
        
# a second or two into the main menu is a good time to preload some stuff
# we'll need elsewhere to avoid hitches later on..
def _preload1():
    for m in ['plasticEyesTransparent', 'playerLineup1Transparent',
              'playerLineup2Transparent', 'playerLineup3Transparent',
              'playerLineup4Transparent', 'angryComputerTransparent',
              'scrollWidgetShort', 'windowBGBlotch']: bs.getModel(m)
    for t in ["playerLineup","lock"]: bs.getTexture(t)
    for tex in ['iconRunaround', 'iconOnslaught',
                'medalComplete', 'medalBronze', 'medalSilver',
                'medalGold', 'characterIconMask']: bs.getTexture(tex)
    bs.getTexture("bg")
    bs.Powerup.getFactory()
    bs.gameTimer(100,_preload2)

def _preload2():
    # FIXME - could integrate these loads with the classes that use them
    # so they don't have to redundantly call the load
    # (even if the actual result is cached)
    for m in ["powerup", "powerupSimple"]: bs.getModel(m)
    for t in ["powerupBomb", "powerupSpeed", "powerupPunch",
              "powerupIceBombs", "powerupStickyBombs", "powerupShield",
              "powerupImpactBombs", "powerupHealth"]: bs.getTexture(t)
    for s in ["powerup01", "boxDrop", "boxingBell", "scoreHit01",
              "scoreHit02", "dripity", "spawn", "gong"]: bs.getSound(s)
    bs.Bomb.getFactory()
    bs.gameTimer(100,_preload3)

def _preload3():
    for m in ["bomb", "bombSticky", "impactBomb"]: bs.getModel(m)
    for t in ["bombColor", "bombColorIce", "bombStickyColor",
              "impactBombColor", "impactBombColorLit"]: bs.getTexture(t)
    for s in ["freeze", "fuse01", "activateBeep", "warnBeep"]: bs.getSound(s)
    spazFactory = bs.Spaz.getFactory()
    # go through and load our existing spazzes and their icons
    # (spread these out quite a bit since theres lots of stuff for each)
    def _load(spaz):
        spazFactory._preload(spaz)
        # icons also..
        bs.getTexture(bsSpaz.appearances[spaz].iconTexture)
        bs.getTexture(bsSpaz.appearances[spaz].iconMaskTexture)
    # FIXME - need to come up with a standin texture mechanism or something
    # ..preloading won't scale too much farther..
    t = 50
    bs.gameTimer(200,_preload4)

def _preload4():
    for t in ['bar', 'meter', 'null', 'flagColor', 'achievementOutline']:
        bs.getTexture(t)
    for m in ['frameInset', 'meterTransparent', 'achievementOutline']:
        bs.getModel(m)
    for s in ['metalHit', 'metalSkid', 'refWhistle', 'achievement']:
        bs.getSound(s)
    bs.Flag.getFactory()
    bs.Powerup.getFactory()

class SplashScreenActivity(bs.Activity):

    def __init__(self,settings={}):
        bs.Activity.__init__(self,settings)
        self._part1Duration = 4000
        self._tex = bs.getTexture('aliSplash')
        self._tex2 = bs.getTexture('aliControllerQR')
        
    def _startPreloads(self):
        # FIXME - the func that calls us back doesn't save/restore state
        # or check for a dead activity so we have to do that ourself..
        if self.isFinalized(): return
        with bs.Context(self): _preload1()
        
    def onTransitionIn(self):
        import bsInternal
        bs.Activity.onTransitionIn(self)
        bsInternal._addCleanFrameCallback(bs.WeakCall(self._startPreloads))
        self._background = bsUtils.Background(fadeTime=500, startFaded=True,
                                              showLogo=False)
        self._part = 1
        self._image = bsUtils.Image(self._tex, transition='fadeIn',
                                    modelTransparent=bs.getModel('image4x1'),
                                    scale=(800, 200), transitionDelay=500,
                                    transitionOutDelay=self._part1Duration-1300)
        bs.gameTimer(self._part1Duration, self.end)

    def _startPart2(self):
        if self._part != 1: return
        self._part = 2
        self._image = bsUtils.Image(self._tex2, transition='fadeIn',
                                    scale=(400, 400), transitionDelay=0)
        t = bsUtils._translate('tips', 'If you are short on controllers, '
                               'install the \'${REMOTE_APP_NAME}\' app\n'
                               'on your mobile devices to use them '
                               'as controllers.')
        t = t.replace('${REMOTE_APP_NAME}',bsUtils._getRemoteAppName())
        self._text = bsUtils.Text(t, maxWidth=900, hAlign='center',
                                  vAlign='center', position=(0,270),
                                  color=(1,0,1,1), transition='fadeIn')
    def onSomethingPressed(self):
        self.end()

gFirstRun = True

class MainMenuSession(bs.Session):

    def __init__(self):
        bs.Session.__init__(self)
        self._locked = False
        # we have a splash screen only on ali currently..
        env = bs.getEnvironment()
        global gFirstRun
        if env['platform'] == 'android' \
           and env['subplatform'] == 'alibaba' \
           and gFirstRun:
            bsInternal._lockAllInput()
            self._locked = True
            self.setActivity(bs.newActivity(SplashScreenActivity))
            gFirstRun = False
        else:
            self.setActivity(bs.newActivity(MainMenuActivity))

    def onActivityEnd(self,activity,results):
        if self._locked:
            bsInternal._unlockAllInput()
        # any ending activity leads us into the main menu one..
        self.setActivity(bs.newActivity(MainMenuActivity))
        
    def onPlayerRequest(self,player):
        # reject player requests, but if we're in a splash-screen, take the
        # opportunity to tell it to leave
        # FIXME - should add a blanket way to capture all input for
        # cases like this
        activity = self.getActivity()
        if isinstance(activity, SplashScreenActivity):
            with bs.Context(activity): activity.onSomethingPressed()
        return False


################Objects##########
        
class Box(bs.Actor):
    def __init__(self,position=(0,0,0),texture=None):
        bs.Actor.__init__(self)
        self.node = bs.newNode('prop',
                               delegate=self,
                               attrs={'position':position,
                                      'velocity':(0,0,0),
                                      'model':bs.getModel('powerup'),
                                      'modelScale':8.0,
                                      'bodyScale':7 ,
									  'density':999999999999999999999,
									  'damping':999999999999999999999,
                                      'gravityScale':0,
                                      'sticky':True, 
                                      'body':'crate',
                                      'reflection':'powerup',
                                      'reflectionScale':[0.3],									  
                                      'colorTexture':bs.getTexture(texture),
                                      'materials':[bs.getSharedObject('footingMaterial')]})