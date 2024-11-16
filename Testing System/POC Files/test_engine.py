from pipython import GCSDevice

with GCSDevice('E-873') as controller:
    controller.InterfaceSetupDlg()

    axis = 1

    import ipdb; ipdb.set_trace()