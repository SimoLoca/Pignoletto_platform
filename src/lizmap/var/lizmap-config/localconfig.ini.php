;<?php die(''); ?>
;for security reasons , don't remove or modify the first line

; put here configuration variables that are specific to this installation


; chmod for files created by Lizmap and Jelix
;chmodFile=0664
;chmodDir=0775



[modules]
;; uncomment it if you want to use ldap for authentication
;; see documentation to complete the ldap configuration
;ldapdao.access=2


jcommunity.installparam=manualconfig
wps.access=2
[coordplugin_auth]
;; uncomment it if you want to use ldap for authentication
;; see documentation to complete the ldap configuration
;driver=ldapdao

[wps]
wps_rootUrl="http://wps:8080/"
ows_url="http://map:8080/ows/"
wps_rootDirectories="/srv/projects"
redis_host=redis
redis_port=6379
redis_db=1
redis_key_prefix=wpslizmap


[coordplugins]
lizmap=lizmapConfig.ini.php
