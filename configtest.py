import yaml

config_file = "config.yaml"
octoprint_config = "testenv/testconfig/config.yaml"
bot_details = {}
try:
    with open(config_file, "r") as config:
        bot_details  = yaml.load(config.read())
except:
    print("To test discord bot posting, you need to create a file "
              "called config.yaml in the root directory with your bot "
              "details. NEVER COMMIT THIS FILE.")
    exit()

octo_config = {}
try:
    with open(octoprint_config, "r") as config:
        octo_config = yaml.load(config.read())
except:
    print("Run the test.[sh|bat] script first to initialise the testenv.")
    exit()

octo_config['plugins']['discordremote'] = bot_details

with open(octoprint_config, "w") as config:
    yaml.safe_dump(octo_config, stream=config, default_flow_style=False, indent="  ", allow_unicode=True)

