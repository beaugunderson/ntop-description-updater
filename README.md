ntop-description-updater
========================

This may be useful to you if:

-    You run dd-wrt on your home router
-    You use rflowd to push traffic flows to nTop on another computer
-    You wish you could use dd-wrt's `macupd` service to keep the descriptions of your nTop installation up to date

If you define a MAC address like "aa:bb:cc:dd:ee:ff" to have a description "Jim's desktop" then `ntop-description-updater` will happily listen on port 2056 and wait for `macupd` to tell it what the current IP address for "aa:bb:cc:dd:ee:ff" is.

If `macupd` tells it that "aa:bb:cc:dd:ee:ff" currently has IP address 192.168.1.101 then `ntop-description-updater` will set the preference key "hostname.192.168.1.101" to "Jim's desktop".