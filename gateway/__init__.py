"""MHub test-automation framework (Page Object Model).

Package layout mirrors the sibling automation demos
(``appium-automation-framework-demo`` / ``cypress-automation-framework-demo``):

    config/    ConfigReader              # externalised config (env-overridable)
    driver/    DriverFactory             # builds the MQTT session from config
               DriverManager             # thread-local session (parallel-safe)
    base/      BasePage                  # reusable publish/request/wait actions
    pages/     ScenePage, NodeControlPage, ConfigurationPage, AutomationPage
    protocol/  messages, topics          # the MHub wire format
"""
