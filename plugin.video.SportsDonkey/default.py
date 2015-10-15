import base64,urllib,urllib2,re,cookielib,string,os,xbmc, xbmcgui, xbmcaddon, xbmcplugin, random, datetime,urlparse,mknet
from resources.libs.common_addon import Addon

addon_id        = 'plugin.video.SportsDonkey'
selfAddon       = xbmcaddon.Addon(id=addon_id)
datapath        = xbmc.translatePath(selfAddon.getAddonInfo('profile'))
fanart          = xbmc.translatePath(os.path.join('special://home/addons/' + addon_id , 'fanart.jpg'))
icon            = xbmc.translatePath(os.path.join('special://home/addons/' + addon_id, 'icon.png'))
art 		= xbmc.translatePath(os.path.join('special://home/addons/' + addon_id + '/resources/art/'))
user            = selfAddon.getSetting('hqusername')
passw           = selfAddon.getSetting('hqpassword')
cookie_file     = os.path.join(os.path.join(datapath,''), 'SD.lwp')
cookie_file2    = os.path.join(os.path.join(datapath,''), 'DS.lwp')
net             = mknet.Net()

if user == '' or passw == '' or user == 'Droidsticks':
    if os.path.exists(cookie_file):
        os.remove(cookie_file)
    try:
        AddonList = ['plugin.video.aswizard', 'plugin.video.UpdateWizard']
        for addons in AddonList:
            wizardpath = xbmc.translatePath(os.path.join('special://home/userdata/addon_data/'+addons, 'settings.xml'))
            if os.path.exists(wizardpath):
                wizset = open(wizardpath, 'r')
                wizlog = wizset.read()
                wizuser = re.compile('<setting id="dsusername" value="(.+?)"').findall(wizlog)[0]
                wizpass = re.compile('<setting id="dspassword" value="(.+?)"').findall(wizlog)[0]
                amemberurl = 'http://dswizard.co/amember/member'
                hqpass = 'http://dswizard.co/amember/content/f/id/8/'
                html = net.http_GET(amemberurl).content
                r = re.findall(r'<input type="hidden" name="(.+?)" value="(.+?)" />', html, re.I)
                post_data = {}
                post_data['amember_login'] = wizuser
                post_data['amember_pass'] = wizpass
                for name, value in r:
                    post_data[name] = value
                    net.http_GET(amemberurl)
                    net.http_POST(amemberurl,post_data)
                    net.save_cookies(cookie_file)
                    net.set_cookies(cookie_file)
                    response = net.http_GET(amemberurl)
        if 'Logged in as' in response.content:
                response = net.http_GET(hqpass)
                link = response.content
                user=re.compile('<username>(.+?)</username>').findall(link)[0]
                passw=re.compile('<password>(.+?)</password>').findall(link)[0]
    except:
        dialog = xbmcgui.Dialog()
        ret = dialog.yesno('Sports Donkey', 'Please enter your Sports Donkey account details','or register if you dont have an account','at http://sportsdonkey.club','Cancel','Login')
        if ret == 1:
            keyb = xbmc.Keyboard('', 'Enter Username')
            keyb.doModal()
            if (keyb.isConfirmed()):
                search = keyb.getText()
                username=search
                keyb = xbmc.Keyboard('', 'Enter Password:')
                keyb.doModal()
                if (keyb.isConfirmed()):
                   search = keyb.getText()
                   password=search
                   selfAddon.setSetting('hqusername',username)
                   selfAddon.setSetting('hqpassword',password)
        else:quit()
        user = selfAddon.getSetting('hqusername')
        passw = selfAddon.getSetting('hqpassword')

#############################################################################################################################

def setCookie(srDomain):
    html = net.http_GET(srDomain).content
    r = re.findall(r'<input type="hidden" name="(.+?)" value="(.+?)" />', html, re.I)
    post_data = {}
    post_data['amember_login'] = user
    post_data['amember_pass'] = passw
    for name, value in r:
        value = value.replace('https','http')
        post_data[name] = value
    net.http_GET('http://sportsdonkey.club/site/member')
    net.http_POST('http://sportsdonkey.club/site/member',post_data)
    net.save_cookies(cookie_file)
    net.set_cookies(cookie_file)
   
def Index():
    setCookie('http://sportsdonkey.club/site/member')
    response = net.http_GET('http://sportsdonkey.club/site/live/')
    if not 'http://sportsdonkey.club/site/logout' in response.content:
        dialog = xbmcgui.Dialog()
        dialog.ok('Sports Donkey', 'Login Error','An error ocurred logging in. Please check your details','Ensure your account is active at http://sportsdonkey.club')
        quit()
    addDir('Calendar','url',6,icon,fanart)
    addDir('Live Streams','url',1,icon,fanart)
    addDir('Video on Demand','http://sportsdonkey.club/site/live/vod/',4,icon,fanart)
    lasttweet = twitter()
    addLink('','url','mode',art+'black.png',fanart)
    addLink('[COLOR blue]@Sports_Donkey - Follow us on Twitter for the latest updates [/COLOR]','url','mode',icon,fanart)
    addLink('[COLOR blue]Latest Tweet: [/COLOR]'+lasttweet,'url','mode',icon,fanart)

    
def live():
    setCookie('http://sportsdonkey.club/site/member')
    response = net.http_GET('http://sportsdonkey.club/site/live/')
    link = response.content
    link = cleanHex(link)
    link=link.replace('onclick=SwitchMenu','\nonclick=SwitchMenu')
    cats=re.compile("\('.+?'\)>(.+?)</div>").findall(link)
    for name in cats:
        addDir(name,name,2,icon,fanart)

def getchannels(name,url):
    setCookie('http://sportsdonkey.club/site/member')
    response = net.http_GET('http://sportsdonkey.club/site/live/')
    link = response.content
    link = cleanHex(link)
    link=link.replace('onclick=SwitchMenu','\nonclick=SwitchMenu').replace('</a><br ','')
    match=re.compile("onclick=SwitchMenu(.+?)\n").findall(link)
    print match
    for catdata in match:
        cats=re.compile("\('.+?'\)>(.+?)</div>").findall(catdata)
        for catname in cats:
            if catname == name:
                channels=re.compile("<a href=(.+?)>(.+?)/>").findall(catdata)
                for url, name in channels:
                    url = 'http://sportsdonkey.club/site/live/'+url
                    addLink(name,url,3,icon,fanart)
                    
def playstream(url,name):
    setCookie('http://sportsdonkey.club/site/member')
    response = net.http_GET(url)
    link = response.content
    link = cleanHex(link)
    strurl=re.compile("file: '(.+?)',").findall(link)[0]
    ok=True
    liz=xbmcgui.ListItem(name, iconImage=icon,thumbnailImage=icon); liz.setInfo( type="Video", infoLabels={ "Title": name } )
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
    if 'rtmp' in strurl:
        strurl=strurl + ' live=true timeout=20'
    xbmc.Player ().play(strurl, liz, False)
       
def vod(url):
    setCookie('http://sportsdonkey.club/site/member')
    net.set_cookies(cookie_file)
    response = net.http_GET(url)
    link = response.content
    link = cleanHex(link)
    if 'pid=' in link:
       match=re.compile("<a href=(.+?)>(.+?)</a>").findall(link)[7:]
       print match
       for url,name in match:
           url='http://sportsdonkey.club/site/live/vod/'+url
           addLink(name,url,3,icon,fanart)
    else:
        link=link.replace('onclick=SwitchMenu','\nonclick=SwitchMenu')
        cats=re.compile("\('.+?'\)>(.+?)</div>").findall(link)
        for name in cats:
            addDir(name,url,5,icon,fanart)

def vodfolders(url,name):
    setCookie('http://sportsdonkey.club/site/member')
    net.set_cookies(cookie_file)
    if url==name:
        response = net.http_GET('http://sportsdonkey.club/site/live/vod/')
    else:
        response = net.http_GET(url)
    link = response.content
    link = cleanHex(link)
    link=link.replace('onclick=SwitchMenu','\nonclick=SwitchMenu').replace('</a><br ','')
    match=re.compile("onclick=SwitchMenu(.+?)\n").findall(link)
    for catdata in match:
        cats=re.compile("\('.+?'\)>(.+?)</div>").findall(catdata)
        for catname in cats:
            if catname == name:
                channels=re.compile("<a href=(.+?)>(.+?)/>").findall(catdata)
                for url, name in channels:
                    url = 'http://sportsdonkey.club/site/live/vod/'+url
                    addDir(name,url,4,icon,fanart)

def schedule():
    addLink('[COLOR red]Notice: The fixtures and calendar are updated on a Thursday afternoon/evening. (GMT time)[/COLOR]','url','mode',art+'black.png',fanart)
    addLink('','url','mode',art+'black.png',fanart)
    net.set_cookies(cookie_file)
    response = net.http_GET('http://sportsdonkey.club/calendar')
    link = response.content
    link=link.replace('\r','').replace('\n','').replace('\t','').replace('&nbsp;','').replace('  ','')
    i=0
    cal=re.compile('<ul class="resp-tabs-list">(.+?)<div class').findall(link)[0]
    days=re.compile('<li>(.+?)</li>').findall(cal)
    for day in days:
        days[i]='[COLOR white][B]'+days[i]+'[/B][/COLOR]'
        addLink(days[i],'url','mode',art+'white.png',fanart)
        events=re.compile("<\!-- Fixtures -->(.+?)</section>").findall(link)[0]
        dayevents=re.compile("<div><div class='sidebarbox-title'>(.+?)</a></div></div>").findall(events)[i]
        eventsforday=re.compile("fixture-row-left'>(.+?)</div></div><div class='fixture-row-right'>(.+?)</div>").findall(dayevents)    
        for name,channel in eventsforday:
            name=name.replace('<div>',' - ')
            name = '[COLOR white]'+name+'[/COLOR]'
            addLink(name + ' - ' + channel,'url','mode',art+'black.png',fanart)
        i=i+1       
    xbmc.executebuiltin('Container.SetViewMode(51)')

def twitter():
        twit = 'https://script.google.com/macros/s/AKfycbyBcUa5TlEQudk6Y_0o0ZubnmhGL_-b7Up8kQt11xgVwz3ErTo/exec?607560445139030017'
        response = net.http_GET(twit)
        link = response.content
        link = link.replace('/n','')
        link = link.encode('ascii', 'ignore').decode('ascii').decode('ascii').replace('&#39;','\'').replace('&#xA0;','').replace('&#x2026;','').replace('amp;','')
        lasttweet=re.compile("<title>(.+?)</title>").findall(link)[1]
        return lasttweet
    
        
        
  
def addDir(name,url,mode,iconimage,fanart,description=''):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&description="+str(description)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name, 'plot': description } )
        liz.setProperty('fanart_image', fanart)
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

def addLink(name,url,mode,iconimage,fanart,description=''):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&description="+str(description)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name, 'plot': description } )
        liz.setProperty('fanart_image', fanart)
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
        return ok
    
def cleanHex(text):
    def fixup(m):
        text = m.group(0)
        if text[:3] == "&#x": return unichr(int(text[3:-1], 16)).encode('utf-8')
        else: return unichr(int(text[2:-1])).encode('utf-8')
    return re.sub("(?i)&#\w+;", fixup, text.decode('ISO-8859-1').encode('utf-8'))

def notification(title, message, ms, nart):
    xbmc.executebuiltin("XBMC.notification(" + title + "," + message + "," + ms + "," + nart + ")")

def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
                                
        return param
              
params=get_params(); url=None; name=None; mode=None; iconimage=None
try:url=urllib.unquote_plus(params["url"])
except:pass
try:name=urllib.unquote_plus(params["name"])
except:pass
try:mode=int(params["mode"])
except:pass
try:iconimage=urllib.unquote_plus(params["iconimage"])
except:pass

print "Mode: "+str(mode); print "Name: "+str(name); print "Thumb: "+str(iconimage)
if mode==None or url==None or len(url)<1:Index()
elif mode==1:live()
elif mode==2:getchannels(name,url)
elif mode==3:playstream(url,name)
elif mode==4:vod(url)
elif mode==5:vodfolders(url,name)
elif mode==6:schedule()
        
xbmcplugin.endOfDirectory(int(sys.argv[1]))
