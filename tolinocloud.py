# tolino cloud access module

# Hey, tolino developers at Telekom / T-Systems:
#
# This client wants to be a friendly citizen within the tolino cloud.
# It accesses the javascript / REST api of pageplace.de and
# does so in a responsible manner, no hacking involved.
#
# It works, but it would be nice if you could look at the
# "Hey, tolino developers" comments in this code. I'm grateful for
# some hints to make this code work better for your service.


# Copyright (C) 2014 Hanno Zulla
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.


import platform
import json
import base64
import requests
import re
from urllib.parse import urlparse, parse_qs

class TolinoException(Exception):
    pass


class TolinoCloud:

    def _hardware_id():
    
        # tolino wants to know a few details about the HTTP client hardware
        # when it connects.
        #
        # 1233X-44XXX-XXXXX-XXXXX-XXXXh
        #
        # 1  = os id
        # 2  = browser engine id
        # 33 = browser id
        # 44 = browser version
        # X  = the result of a fingerprinting image
    
        os_id = {
            'Windows' : '1',
            'Darwin'  : '2',
            'Linux'   : '3'
            }.get(platform.system(), 'x')
        
        # The hardware id contains some info about the browser
        #
        # Hey, tolino developers: Let me know which id values to use here
        engine_id  = 'x'
        browser_id = 'xx'
        version_id = '00'
        
        # For some odd reason, the tolino javascript draws the text
        # "www.tolino.de" and a rectangle filled with the offical Telekom
        # magenta #E20074 (http://de.wikipedia.org/wiki/Magenta_%28Farbe%29)
        # into an image canvas and then fuddles around with the
        # base64-encoded PNG. Probably to gain some sort of fingerprint,
        # but it's not quite clear how this would help the tolino API.
        #
        # Hey, tolino developers: Let me know what you need here.
    
        fingerprint = 'ABCDEFGHIJKLMNOPQR'
        
        return (os_id +
            engine_id +
            browser_id +
            fingerprint[0:1] +
            '-' +
            version_id +
            fingerprint[1:4] +
            '-' +
            fingerprint[4:9] +
            '-' +
            fingerprint[9:14] +
            '-' +
            fingerprint[14:18] +
            'h')

    hardware_id = _hardware_id()
    
    partner_mapping = {
         3 : 'Thalia.de',
         6 : 'Buch.de',
        13 : 'Hugendubel.de'
        # TODO: more to come
    }
    
    partner_settings = {
         3: {
            'partner'          : 'Thalia.de',
            'client_id'        : 'webshop01',
            'scope'            : 'SCOPE_BOSH SCOPE_BUCHDE',
            'signup_url'       : 'https://ssl.thalia.de/shop/home/kunde/neu/',
            'profile_url'      : 'https://ssl.thalia.de/shop/home/kunde/',
            'login_url'        : 'https://ssl.thalia.de/shop/home/login/dologin/',
            'login_form'       : {
                'username' : 'username',
                'password' : 'password',
                'extra'    : {}
             },
            'login_cookie'     : 'KUNDE',
            'tat_url'          : 'https://ssl.thalia.de/shop/home/ebook/anzeigen/',
            'logout_url'       : 'https://ssl.thalia.de/shop/home/login/logout/',
            'reader_url'       : 'https://html5reader.thalia.de/library/library.html#!/library',
            'register_url'     : 'https://bosh.pageplace.de/bosh/rest/registerhw',
            'devices_url'      : 'https://bosh.pageplace.de/bosh/rest/handshake/devices/list',
            'unregister_url'   : 'https://bosh.pageplace.de/bosh/rest/handshake/devices/delete',
            'upload_url'       : 'https://bosh.pageplace.de/bosh/rest/upload',
            'delete_url'       : 'https://bosh.pageplace.de/bosh/rest/deletecontent',
            'inventory_url'    : 'https://bosh.pageplace.de/bosh/rest/inventory/delta',
            'downloadinfo_url' : 'https://bosh.pageplace.de/bosh/rest//cloud/downloadinfo/{}/{}/type/external-download'
            },
         6: {
            'partner'          : 'Buch.de',
            'client_id'        : 'webshop01',
            'scope'            : 'SCOPE_BOSH SCOPE_BUCHDE',
            'signup_url'       : 'https://ssl.buch.de/shop/home/kunde/neu/',
            'profile_url'      : 'https://ssl.buch.de/shop/home/kunde/',
            'login_url'        : 'https://ssl.buch.de/shop/home/login/dologin/',
            'login_form'       : {
                'username' : 'username',
                'password' : 'password',
                'extra'    : {}
             },
            'login_cookie'     : 'KUNDE',
            'tat_url'          : 'https://ssl.buch.de/shop/home/ebook/anzeigen/',
            'logout_url'       : 'https://ssl.buch.de/shop/home/login/logout/',
            'reader_url'       : 'https://html5reader.buch.de/library/library.html#!/library',
            'register_url'     : 'https://bosh.pageplace.de/bosh/rest/registerhw',
            'devices_url'      : 'https://bosh.pageplace.de/bosh/rest/handshake/devices/list',
            'unregister_url'   : 'https://bosh.pageplace.de/bosh/rest/handshake/devices/delete',
            'upload_url'       : 'https://bosh.pageplace.de/bosh/rest/upload',
            'delete_url'       : 'https://bosh.pageplace.de/bosh/rest/deletecontent',
            'inventory_url'    : 'https://bosh.pageplace.de/bosh/rest/inventory/delta',
            'downloadinfo_url' : 'https://bosh.pageplace.de/bosh/rest//cloud/downloadinfo/{}/{}/type/external-download'
            },
        13: {
            'partner'          : 'Hugendubel.de',
            'client_id'        : '4c20de744aa8b83b79b692524c7ec6ae',
            'scope'            : 'ebook_library',
            'signup_url'       : 'https://www.hugendubel.de/go/my_my/my_newRegistration/',
            'profile_url'      : 'https://www.hugendubel.de/go/my_my/my_data/',
            'token_url'        : 'https://api.hugendubel.de/rest/oauth2/token',
            'revoke_url'       : 'https://api.hugendubel.de/rest/oauth2/revoke',
            'auth_url'         : 'https://www.hugendubel.de/oauth2/authorize',
            'login_url'        : 'https://www.hugendubel.de/go/my_dry/my_login/lfa/login/receiver_object/my_login/',
            'login_form'       : {
                'username' : 'form[login]',
                'password' : 'form[password]',
                'extra'    : {
                    'form_send' : 1
                }
            },
            'login_cookie'     : 'shop[login]',
            'reader_url'       : 'https://webreader.hugendubel.de/library/library.html#!/library',
            'register_url'     : 'https://bosh.pageplace.de/bosh/rest/registerhw',
            'devices_url'      : 'https://bosh.pageplace.de/bosh/rest/handshake/devices/list',
            'unregister_url'   : 'https://bosh.pageplace.de/bosh/rest/handshake/devices/delete',
            'upload_url'       : 'https://bosh.pageplace.de/bosh/rest/upload',
            'delete_url'       : 'https://bosh.pageplace.de/bosh/rest/deletecontent',
            'inventory_url'    : 'https://bosh.pageplace.de/bosh/rest/inventory/delta',
            'downloadinfo_url' : 'https://bosh.pageplace.de/bosh/rest//cloud/downloadinfo/{}/{}/type/external-download'
        }
    }

    def __init__(self, partner_id):
        self.partner_id = partner_id
        self.session = requests.session()
    
    def login(self, username, password):
        s = self.session;
        c = self.partner_settings[self.partner_id]
        
        # Login with partner site
        # to retrieve site's cookies within browser session
        data = c['login_form']['extra']
        data[c['login_form']['username']] = username
        data[c['login_form']['password']] = password
        r = s.post(c['login_url'], data, verify=False)
        if not c['login_cookie'] in s.cookies:
            raise TolinoException('login to {} failed.'.
                format(self.partner_mapping[self.partner_id]))

        auth_code = ""
        if 'tat_url' in c:
            try:
                r = s.get(c['tat_url'], verify=False)
                b64 = re.search(r'\?tat=(.*?)#library', r.text).group(1)
                self.access_token = base64.b64decode(b64).decode('utf-8')
            except:
                raise TolinoException('oauth access token request failed.')
        else:
            # Request OAUTH code
            r = s.get(c['auth_url'], params = {
                'client_id'     : c['client_id'],
                'response_type' : 'code',
                'scope'         : c['scope'],
                'redirect_uri'  : c['reader_url']
            }, verify=False, allow_redirects=False)
            try:
                params = parse_qs(urlparse(r.headers['Location']).query)
                auth_code = params['code'][0]
            except:
                raise TolinoException('oauth code request failed.')
        
            # Fetch OAUTH access token
            r = s.post(c['token_url'], data = {
                'client_id'    : c['client_id'],
                'grant_type'   : 'authorization_code',
                'code'         : auth_code,
                'scope'        : c['scope'],
                'redirect_uri' : c['reader_url']
            }, verify=False, allow_redirects=False)
            try:
                j = r.json()
                self.access_token = j['access_token']
                self.refresh_token = j['refresh_token']
                self.token_expires = int(j['expires_in'])
            except:
                raise TolinoException('oauth access token request failed.')
    
    def logout(self):
        s = self.session;
        c = self.partner_settings[self.partner_id]

        if 'revoke_url' in c:
            r = s.post(c['revoke_url'],
                data = {
                    'client_id'  : c['client_id'],
                    'token_type' : 'refresh_token',
                    'token'      : self.refresh_token
                }
            )
            if r.status_code != 200:
                raise TolinoException('logout failed.')
        else:
            r = s.post(c['logout_url'])
            if r.status_code != 200:
                raise TolinoException('logout failed.')


    def register(self):
        s = self.session;
        c = self.partner_settings[self.partner_id]

        # Register our hardware
        r = s.post(c['register_url'],
            data = json.dumps({
                'initAppRequest':{
                    'hardware_id'   : TolinoCloud.hardware_id,
                    'hardware_type' : 'HTML5_1',
                    'client_type'   : 'HTML5_1',
                    'hardware_name' : 'other'
                }
            }),
            headers = {
                'content-type': 'application/json',
                't_auth_token': self.access_token,
                'hardware_id' : TolinoCloud.hardware_id,
                'm_id'        : self.partner_id
            }
        )
        if r.status_code != 200:
            raise TolinoException('register {} failed.'.format(device_id))
        
    def unregister(self, device_id = hardware_id):
        s = self.session;
        c = self.partner_settings[self.partner_id]

        r = s.post(c['unregister_url'],
            data = json.dumps({
                'deleteDevicesRequest':{
                    'accounts' : [ {
                        'auth_token'  : self.access_token,
                        'reseller_id' : self.partner_id
                    } ],
                    'devices'  : [ {
                        'device_id'   : device_id,
                        'reseller_id' : self.partner_id
                    } ]
                }
            }),
            headers = {
                'content-type': 'application/json',
                't_auth_token': self.access_token,
                'm_id'        : self.partner_id
            }
        )
        if r.status_code != 200:
            try:
                j = r.json()
                raise TolinoException('unregister {} failed: {}'.format(device_id, j['ResponseInfo']['message']))
            except KeyError:
                raise TolinoException('unregister {} failed: reason unknown.'.format(device_id))

    def devices(self):
        s = self.session;
        c = self.partner_settings[self.partner_id]

        r = s.post(c['devices_url'],
            data = json.dumps({
                'deviceListRequest':{
                    'accounts' : [ {
                        'auth_token'  : self.access_token,
                        'reseller_id' : self.partner_id
                    } ]
                }
            }),
            headers = {
                'content-type': 'application/json',
                't_auth_token': self.access_token,
                'm_id'        : self.partner_id
            }
        )
        if r.status_code != 200:
            raise TolinoException('device list request failed.')

        try:
            devs = []
            j = r.json()
            for item in j['deviceListResponse']['devices']:
                devs.append({
                    'id'         : item['deviceId'],
                    'name'       : item['deviceName'],
                    'type'       : {
                        'unknown_imx50_rdp_1' : 'tolino shine',
                        'tolino_vison'        : 'tolino vision',
                        'HTML5_1'             : 'web browser'
                        }.get(item['deviceType'], item['deviceType']),
                    'partner'    : int(item['resellerId']),
                    'registered' : int(item['deviceRegistered']),
                    'lastusage'  : int(item['deviceLastUsage'])
                })
            return devs
        except:
            raise TolinoException('device list request failed.')

    def _parse_metadata(self, j):
        try:
            return {
                'partner'     : int(j['resellerId']),
                'id'          : j['epubMetaData']['identifier'],
                'title'       : j['epubMetaData']['title'],
                'subtitle'    : j['epubMetaData']['subtitle'],
                'author'      : [a['name'] for a in j['epubMetaData']['author']],
                'mime'        : j['epubMetaData']['deliverable'][0]['contentFormat'],
                'type'        : j['epubMetaData']['type'].lower(),
                'issued'      : self._optionalInt(j['epubMetaData']['issued']),
                'purchased'   : int(j['epubMetaData']['deliverable'][0]['purchased'])
            }
        except:
            raise TolinoException('could not parse metadata')

    def _optionalInt(self, i):
        try:
            return int(i)
        except TypeError:
            return None
        
    def inventory(self):
        s = self.session;
        c = self.partner_settings[self.partner_id]

        r = s.get(c['inventory_url'],
            params = {'strip': 'true'},
            headers = {
                't_auth_token' : self.access_token,
                'hardware_id'  : TolinoCloud.hardware_id,
                'm_id'         : self.partner_id
            }
        )
        if r.status_code != 200:
            raise TolinoException('inventory list request failed.')

        try:
            inv = []
            j = r.json()
            # edata = own documents uploaded to Tolino Cloud
            for item in j['PublicationInventory']['edata']:
                inv.append(self._parse_metadata(item))
            # ebook = purchased ebooks in Tolino Cloud
            for item in j['PublicationInventory']['ebook']:
                inv.append(self._parse_metadata(item))
            return inv
        except:
            raise TolinoException('inventory list request failed.')
    
    def upload(self, filename):
        s = self.session;
        c = self.partner_settings[self.partner_id]

        name = filename.split('/')[-1]
        ext = filename.split('.')[-1]
        
        mime = {
            'pdf'  : 'application/pdf',
            'epub' : 'application/epub+zip'
        }.get(ext.lower(), 'application/pdf')
        
        r = s.post(c['upload_url'],
            files = [('file', (name, open(filename, 'rb'), mime))],
            headers = {
                't_auth_token' : self.access_token,
                'hardware_id'  : TolinoCloud.hardware_id,
                'm_id'         : self.partner_id
            }
        )
        if r.status_code != 200:
            raise TolinoException('file upload failed.')

        try:
            j = r.json()
            return j['metadata']['deliverableId']
        except:
            raise TolinoException('file upload failed.')
    
    def delete(self, id):
        s = self.session;
        c = self.partner_settings[self.partner_id]

        r = s.get(c['delete_url'],
            params = {
                'deliverableId': id
            },
            headers = {
                't_auth_token' : self.access_token,
                'hardware_id'  : TolinoCloud.hardware_id,
                'm_id'         : self.partner_id
            }
        )
        if r.status_code != 200:
            try:
                j = r.json()
                raise TolinoException('delete {} failed: {}'.format(id, j['ResponseInfo']['message']))
            except KeyError:
                raise TolinoException('delete {} failed: reason unknown.'.format(id))

    def download_info(self, id):
        s = self.session;
        c = self.partner_settings[self.partner_id]

        b64 = base64.b64encode(bytes(id, 'utf-8')).decode('utf-8')
        r = s.get(c['downloadinfo_url'].format(b64, b64),
            headers = {
                't_auth_token' : self.access_token,
                'hardware_id'  : TolinoCloud.hardware_id,
                'm_id'         : self.partner_id
            }
        )
        if r.status_code != 200:
            raise TolinoException('download info request failed.')

        j = r.json()
        url = j['DownloadInfo']['contentUrl']
        return {
            'url'      : url,
            'filename' : url.split('/')[-1],
            'filetype' : j['DownloadInfo']['format'],
        }

    def download(self, path, id):
        s = self.session;
        c = self.partner_settings[self.partner_id]

        di = self.download_info(id)

        r = s.get(di['url'],
            stream=True,
            headers = {
                't_auth_token' : self.access_token,
                'hardware_id'  : TolinoCloud.hardware_id,
                'm_id'         : self.partner_id
            }
        )
        if r.status_code != 200:
            try:
                j = r.json()
                raise TolinoException('download request failed: {}'.format(j['ResponseInfo']['message']))
            except KeyError:
                raise TolinoException('download request : reason unknown.')


        filename = path + '/' + di['filename'] if path else di['filename']
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024): 
                if chunk:
                    f.write(chunk)
            f.flush()
        
        return filename
