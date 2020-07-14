cd configuration\src\configuration_manager
START configuration_manager_ecc.bat
cd ..\..\..\

cd notification\src\notification_manager
START notification_manager_ecc.bat
cd ..\..\..\

cd registration\src\registration_manager
START registration_manager_ecc.bat
cd ..\..\..\

cd heartbeat\src\heartbeat_manager
START heartbeat_manager_ecc.bat
cd ..\..\..\

cd download\src\download_manager
START download_manager_ecc.bat
cd ..\..\..\

cd email\src\email_manager
START email_manager_ecc.bat
cd ..\..\..\

cd history\src\history_manager
START history_manager.bat
cd ..\..\..\

cd sensor\src\sensor_manager
START sensor_manager_ecc.bat
cd ..\..\..\

cd ota\src\ota_manager
START ota_manager_ecc.bat
cd ..\..\..\

cd redis\src
START redis.bat
cd ..\..\

cd webapp\src
START webapp.bat
cd ..\..\

cd restapi\src
rest_api.bat

pause