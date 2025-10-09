- If u change cloud vm's for consistency firstly push terraform changes, wait for CI/CD and then only push code that builds and deploy the project (it works anyway, but for consistency it is better to do as was said)

- if machine was recreated it were assigned with new IP, so need to change SSH_HOST secret and change ansible_host in ansible inventory file for CI to run and not fail
