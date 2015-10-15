import urllib,urllib2,re,cookielib,string,os,xbmc, xbmcgui, xbmcaddon, xbmcplugin, random
from t0mm0.common.net import Net as net

addon_id        = 'plugin.video.HQZone'
selfAddon       = xbmcaddon.Addon(id=addon_id)
datapath        = xbmc.translatePath(selfAddon.getAddonInfo('profile'))
fanart          = xbmc.translatePath(os.path.join('special://home/addons/' + addon_id , 'fanart.jpg'))
icon            = xbmc.translatePath(os.path.join('special://home/addons/' + addon_id, 'icon.png'))
cookie_file     = os.path.join(os.path.join(datapath,''), 'hqzone.lwp')
user            = selfAddon.getSetting('hqusername')
passw           = selfAddon.getSetting('hqpassword')
art             = xbmc.translatePath(os.path.join('special://home/addons/' + addon_id + '/resources/art/'))
if user == '' or passw == '':
    if os.path.exists(cookie_file):
        try: os.remove(cookie_file)
        except: pass
    dialog = xbmcgui.Dialog()
    ret = dialog.yesno('HQZone', 'Please enter your HQZone account details','or register if you dont have an account','at www.HQZone.Tv','Cancel','Login')
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
user = selfAddon.getSetting('hqusername')
passw = selfAddon.getSetting('hqpassword')

#############################################################################################################################

def Index():
    setCookie('http://straighthost.com/billing/member')
    response = net().http_GET('http://straighthost.com/billing/member')
    if not 'Edit Profile' in response.content:
        dialog = xbmcgui.Dialog()
        dialog.ok('HQZone', 'Invalid login','Please check your HQZone account details in Add-on settings','')
        quit()
    link = response.content
    link = cleanHex(link)
    link=link.replace('\r','').replace('\n','').replace('\t','').replace('&nbsp;','').replace('  ','')
    notification('HQZone', 'Login Successful', '2000',icon)
    xbmc.sleep(1000)
    vip=re.compile('<li><a href="(.+?)">VIP Streams</a>').findall(link)
    if len(vip)>0:
        vip=vip[0]
        addDir('[COLOR gold]VIP[/COLOR] [COLOR red]Streams[/COLOR]','http://straighthost.com/billing/vip/vip.php',2,art+'streams.gif',fanart)
    addDir('#1 KODI Streaming addon #HQZone','url','',icon,fanart)
    addDir('On [COLOR red]Demand[/COLOR]','http://straighthost.com/billing/vip/vod.php',4,art+'streams.gif',fanart)
    addDir('#1 KODI Streaming addon #HQZone','url','',icon,fanart)
    addDir('[COLOR red]Schedule[/COLOR] Events','http://hqzone.tv/forums/calendar.php?c=1&do=displayweek',52,art+'schedule.gif',fanart)
    addLink('[COLOR red]How to become a VIP member[/COLOR]','Purchase VIP at HQZone.tv for all upcoming events'+'\n'+'1 month access $12.00 for one month 30 days access'+'\n'+'3 months access $35.00 for 3 months 90 days of access'+'\n'+'6 months access $75.00 for 6 months 182 days of access',302,art+'subscribe.gif',fanart)
    addLink('[COLOR blue]Twitter[/COLOR] [COLOR red]Feed[/COLOR]','url',100,art+'social.gif',fanart)
    addLink('[COLOR red]@Follow @HQZoneTv[/COLOR] for Big updates and Like us on Facebook','url','',art+'social.gif',fanart)
    addDir('[COLOR red]HQZone[/COLOR] Account Status','url',200,icon,fanart)
    addDir('[COLOR red]HQ Zone[/COLOR] Support','url',300,icon,fanart)
    addLink('[COLOR red]Request[/COLOR] Zone','Visit Twitter or Website to request an event',302,icon,fanart)
    addLink('How to get a [COLOR red]Refund[/COLOR]','To get a refund mention on Twitter'+'\n'+'or Visit Hqzone website'+'\n'+'Or email Hqzone@hotmail.com',302,icon,fanart)
    

def getschedule(url):
    response = net().http_GET(url)
    link = response.content
    link = cleanHex(link)
    link=link.replace('\r','').replace('\n','').replace('\t','').replace('&nbsp;','').replace('  ','')
    match2=re.compile('''<h4 class="blockhead"><a href=".+?">([^<]+)</a></h4>''').findall(link)
    if match2:
        addLink('[COLOR orange]Week of '+match2[0]+'[/COLOR]','url',100,icon,fanart)
    match=re.compile('''<h3><span class="blocksubhead dayname">([^<]+)</span><span class="daynum" style="cursor:pointer" onclick=".+?">([^<]+)</span>(.+?)</li></ul></li>''').findall(link)
    for day,num,data in match:
        addLink('[COLOR blue]'+day+' '+num+'[/COLOR]','url','',icon,fanart)
        match2=re.compile('''<span class="eventtime">([^<]+)</span><a href=".+?" title=".+?>([^<]+)</a>''').findall(data)
        for time,show in match2:
            addLink(show+'  [COLOR yellow]'+time+'[/COLOR]','url',100,icon,fanart)
        #print data
    """for day,num in match:
        addLink('[COLOR blue]'+day+' '+num+'[/COLOR]','url','',icon,fanart)
        match2=re.compile('''<span class="eventtime">([^<]+)</span><a href=".+?" title=".+?>([^<]+)</a>''').findall(link)
        for time,show in match2:
            addLink(show+'  [COLOR yellow]'+time+'[/COLOR]','url',100,icon,fanart)"""


def getchannels(url):
    vip = 0
    if 'vip' in url:
        baseurl = 'http://straighthost.com/billing/vip/'
        vip = 1
    else:baseurl = 'http://straighthost.com/billing/free/'
    setCookie('http://straighthost.com/billing')
    response = net().http_GET(url)
    link = response.content
    link = cleanHex(link)
    link=link.replace('\r','').replace('\n','').replace('\t','').replace('&nbsp;','').replace('  ','')
    match=re.compile('<a href="(.+?)"></br><font color= "\#fff" size="\+1"><b>(.+?)</b>').findall(link)
    match2=re.compile("<a href='(.+?)'></br><font color= '\#fff' size='\+1'><b>(.+?)</b>").findall(link)
    for url,channel in match:
        channel = channel + ':'+ ':'+ ':'+ ':'
        channel = channel.replace('</font>','').replace('Online','[COLOR limegreen]Online[/COLOR]').replace('Offline','[COLOR red]Offline[/COLOR]').replace('online','[COLOR limegreen]Online[/COLOR]').replace('offline','[COLOR red]Offline[/COLOR]')
        channel = channel.replace('**HD**','[COLOR gold]**HD**[/COLOR]').replace('**720p**','[COLOR gold]**720p**[/COLOR]')
        chsplit = channel.split(':')   
        channel = '[COLOR blue]'+chsplit[0]+'[/COLOR]'+' '+chsplit[1]+chsplit[2]
        url = baseurl+url
        if 'Offline' not in channel:
            addLink(channel,url,3,icon,fanart)
    for url,channel in match2:
        channel = channel + ':'+ ':'+ ':'+ ':'
        channel = channel.replace('</font>','').replace('Online','[COLOR limegreen]Online[/COLOR]').replace('Offline','[COLOR red]Offline[/COLOR]').replace('online','[COLOR limegreen]Online[/COLOR]').replace('offline','[COLOR red]Offline[/COLOR]')
        channel = channel.replace('**HD**','[COLOR gold]**HD**[/COLOR]').replace('**720p**','[COLOR gold]**720p**[/COLOR]')
        chsplit = channel.split(':')   
        channel = '[COLOR blue]'+chsplit[0]+'[/COLOR]'+' '+chsplit[1]+chsplit[2]
        url = baseurl+url
        if 'Offline' not in channel:
            addLink(channel,url,3,icon,fanart)

def getstreams(url,name):
    setCookie('http://straighthost.com/billing/member')
    response = net().http_GET(url)
    link = response.content
    link = cleanHex(link)
    link=link.replace('\r','').replace('\n','').replace('\t','').replace('&nbsp;','').replace('  ','')
    swf='http://p.jwpcdn.com/6/11/jwplayer.flash.swf'
    strurl=re.compile("file: '(.+?)',").findall(link)[0]
    playable = strurl+' swfUrl='+swf+' pageUrl='+url+' live=true timeout=20 token=WY846p1E1g15W7s'
    ok=True
    liz=xbmcgui.ListItem(name, iconImage=icon,thumbnailImage=icon); liz.setInfo( type="Video", infoLabels={ "Title": name } )
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
    try:
        xbmc.Player ().play(playable, liz, False)
    except:
        pass

def playVod(name,url):
    vurl=url.split('/vod/')
    stream_url=vurl[0]+'/vod'
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playlist.clear()
    playpath = 'mp4:'+vurl[1]
    listitem = xbmcgui.ListItem(name)
    listitem.setProperty('PlayPath', playpath);
    playlist.add(stream_url,listitem)
    xbmcPlayer = xbmc.Player()
    xbmcPlayer.play(playlist)

def setCookie(srDomain):
        html = net().http_GET(srDomain).content
        r = re.findall(r'<input type="hidden" name="(.+?)" value="(.+?)" />', html, re.I)
        post_data = {}
        post_data['amember_login'] = user
        post_data['amember_pass'] = passw
        for name, value in r:
            post_data[name] = value
        net().http_GET('http://straighthost.com/billing/member')
        net().http_POST('http://straighthost.com/billing/member',post_data)
        net().save_cookies(cookie_file)
        net().set_cookies(cookie_file)
   
def account():
    setCookie('http://straighthost.com/billing/member')
    response = net().http_GET('http://straighthost.com/billing/member')
    link = response.content
    link = cleanHex(link)
    link=link.replace('\r','').replace('\n','').replace('\t','').replace('&nbsp;','').replace('  ','')
    stat = ''
    user=re.compile('<div class="am-user-identity-block">(.+?)<').findall(link)[0]
    user = user+'\n'+' '
    accnt=re.compile('<li><strong>(.+?)</strong>(.+?)</li>').findall(link)
    for one,two in accnt:
        one = '[COLOR blue]'+one+'[/COLOR]'
        stat = stat+' '+one+' '+two+'\n'
    dialog = xbmcgui.Dialog()
    dialog.ok('[COLOR blue]HQZone Account Status[/COLOR]', '',stat,'')
    quit()

def support():
    addLink('Clear Cache','url',5,icon,fanart)
    addLink('Contact Us','url',301,icon,fanart)
    
def supportpop():
    dialog = xbmcgui.Dialog()
    dialog.ok('[COLOR blue]HQZone Account Support[/COLOR]', 'For account queries please contact us at:','@HQZoneTV (via Twitter)','HQZone@hotmail.com (via Email)')
    quit()
       
def vod():
    setCookie('http://straighthost.com/billing/member')
    response = net().http_GET('http://straighthost.com/billing/vip/vod.php')
    link = response.content
    link = cleanHex(link)
    link=link.replace('\r','').replace('\n','').replace('\t','').replace('&nbsp;','').replace('  ','')
    match=re.compile('<a href="(.+?)"></br><font color= "\#fff" size="\+1"><b>(.+?)</b>').findall(link)
    for url,channel in match:
       addDir(channel,'http://straighthost.com/billing/vip/'+channel.replace(' ','').lower()+'.rss',6,icon,fanart)
    
def getvodstreams(url):
    setCookie(url)
    response = net().http_GET(url)
    link = response.content
    link = cleanHex(link)
    link=link.replace('\r','').replace('\n','').replace('\t','').replace('&nbsp;','').replace('  ','')
    match=re.compile('<item><title>([^<]+)</title><description>.+?</description><jwplayer:source file="([^"]+)" /></item>').findall(link)
    for title,stream in match:
       addLink(title,stream,51,icon,fanart)

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
    try :return re.sub("(?i)&#\w+;", fixup, text.decode('ISO-8859-1').encode('utf-8'))
    except:return re.sub("(?i)&#\w+;", fixup, text.encode("ascii", "ignore").encode('utf-8'))

def notification(title, message, ms, nart):
    xbmc.executebuiltin("XBMC.notification(" + title + "," + message + "," + ms + "," + nart + ")")

def showText(heading, text):
    id = 10147
    xbmc.executebuiltin('ActivateWindow(%d)' % id)
    xbmc.sleep(100)
    win = xbmcgui.Window(id)
    retry = 50
    while (retry > 0):
        try:
            xbmc.sleep(10)
            retry -= 1
            win.getControl(1).setLabel(heading)
            win.getControl(5).setText(text)
            return
        except:
            pass

def twitter():
        import time
        text=''
        twit = 'http://twitrss.me/twitter_user_to_rss/?user=@HQZoneTv'
        #twit += '?time=%d' % time.time()
        response = net().http_GET(twit)
        link = response.content
        link=link.replace('[','').replace(']','')
        match=re.compile('<title><.+?CDATA(.+?)></title>.+?<dc:creator><.+?CDATA(.+?)></dc:creator>.+?<pubDate>(.+?)</pubDate>',re.DOTALL).findall(link)
        for status,author, dte in match:
            #status = cleanHex(status)
            dte = '[COLOR blue][B]'+dte+'[/B][/COLOR]'
            dte = dte.replace('+0000','').replace('2014','').replace('2015','')
            text = text+dte+'\n'+status+'\n'+author+'\n'+'\n'
        showText('[COLOR blue][B]@HQZoneTv[/B][/COLOR]', text)
        quit()

def deletecachefiles():
    xbmc_cache_path = os.path.join(xbmc.translatePath('special://home'), 'cache')
    if os.path.exists(xbmc_cache_path)==True:    
        for root, dirs, files in os.walk(xbmc_cache_path):
            file_count = 0
            file_count += len(files)
        # Count files and give option to delete
            if file_count > 0:
                dialog = xbmcgui.Dialog()
                if dialog.yesno("[COLOR blue]Delete XBMC Cache Files[/COLOR]", str(file_count) + " files found", "Do you want to delete them?"):
                    for f in files:
                        try:
                            os.unlink(os.path.join(root, f))
                        except:
                            pass
                    for d in dirs:
                        try:
                            shutil.rmtree(os.path.join(root, d))
                        except:
                            pass
            else:
                pass
    if xbmc.getCondVisibility('system.platform.ATV2'):
        atv2_cache_a = os.path.join('/private/var/mobile/Library/Caches/AppleTV/Video/', 'Other')
        for root, dirs, files in os.walk(atv2_cache_a):
            file_count = 0
            file_count += len(files)
            if file_count > 0:
                dialog = xbmcgui.Dialog()
                if dialog.yesno("[COLOR blue]Delete ATV2 Cache Files[/COLOR]", str(file_count) + " files found in 'Other'", "Do you want to delete them?"):
                
                    for f in files:
                        os.unlink(os.path.join(root, f))
                    for d in dirs:
                        shutil.rmtree(os.path.join(root, d))
            else:
                pass
        atv2_cache_b = os.path.join('/private/var/mobile/Library/Caches/AppleTV/Video/', 'LocalAndRental')
        for root, dirs, files in os.walk(atv2_cache_b):
            file_count = 0
            file_count += len(files)
            if file_count > 0:
                dialog = xbmcgui.Dialog()
                if dialog.yesno("[COLOR blue]Delete ATV2 Cache Files[/COLOR]", str(file_count) + " files found in 'LocalAndRental'", "Do you want to delete them?"):
                    for f in files:
                        os.unlink(os.path.join(root, f))
                    for d in dirs:
                        shutil.rmtree(os.path.join(root, d))
            else:
                pass
    clear_cache()
    dialog = xbmcgui.Dialog()
    dialog.ok("[COLOR blue]Delete Cache[/COLOR]", "All Done", "")
    quit()

def clear_cache():
   
        sql_delete = 'DELETE FROM netcache'
        success = False
        try:
            common.addon.log('-' + HELPER + '- -' + sql_delete, 2)
            self.dbcur.execute( sql_delete )
            self.dbcon.commit()
            success = True
        except Exception, e:
            common.addon.log('-' + HELPER + '- - failure: %s' % e )
            pass         
        finally:
            return success

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

elif mode==2:getchannels(url)
elif mode==3:getstreams(url,name)
elif mode==4:vod()
elif mode==5:deletecachefiles()
elif mode==6:getvodstreams(url)
elif mode==50:getmovies(url)
elif mode==51:playVod(name,url)
elif mode==52:getschedule(url)
elif mode==100:twitter()
elif mode==200:account()
elif mode==300:support()
elif mode==301:supportpop()
elif mode==302:showText(name, url)


        
xbmcplugin.endOfDirectory(int(sys.argv[1]))

