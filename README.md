# resource_keeper
slack bot for semaphore in team

---

## installation

```
(in directory you want to install resource_keeper)
git clone https://github.com/yskn67/resource_keeper.git
cd resource_keeper
vim resource_keeper/conf.toml
(edit slackbot api token)
sh make_upstart_conf.sh
sudo mv resource_keeper.conf /etc/init/
sudo initctl reload-configuration
sudo initctl start resource_keeper
```
