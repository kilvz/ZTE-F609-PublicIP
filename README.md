# ZTE-F609-PublicIP
A python script made to renew WAN IP from ISP if current IP is private

An alternative to [this solution](https://labkom.co.id/mikrotik/solusi-susah-dapat-ip-public-indihome-dengan-menggunakan-script-mikrotik) by using Python and Selenium to automate changing the WAN IP via the router web interface.
An Admin user is needed for it to work.
It works by checking the WAN IP first. If the WAN IP is private (eg. 10.x.x.x, may vary), then it will try change the WAN connection trigger a few times in order to refresh the IP. After the IP is public, it will logout.
