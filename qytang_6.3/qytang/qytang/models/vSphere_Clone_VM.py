from pyVmomi import vim
from pyVim.connect import SmartConnect,SmartConnectNoSSL, Disconnect
import atexit

def wait_for_task(task):
    """ wait for a vCenter task to finish """
    task_done = False
    while not task_done:
        if task.info.state == 'success':
            return task.info.result

        if task.info.state == 'error':
            print("there was an error")
            task_done = True

def get_obj(content, vimtype, name):
    """
    Return an object by name, if name is None the
    first found object is returned
    """
    obj = None
    container = content.viewManager.CreateContainerView(
        content.rootFolder, vimtype, True)
    for c in container.view:
        if name:
            if c.name == name:
                obj = c
                break
        else:
            obj = c
            break

    return obj

def clone_vm(
        content, template, vm_name, si,
        datacenter_name, vm_folder, datastore_name,
        cluster_name, resource_pool, power_on, datastorecluster_name):
    """
    Clone a VM from a template/VM, datacenter_name, vm_folder, datastore_name
    cluster_name, resource_pool, and power_on are all optional.
    """

    # if none git the first one
    datacenter = get_obj(content, [vim.Datacenter], datacenter_name)

    if vm_folder:
        destfolder = get_obj(content, [vim.Folder], vm_folder)
    else:
        destfolder = datacenter.vmFolder

    if datastore_name:
        datastore = get_obj(content, [vim.Datastore], datastore_name)
    else:
        datastore = get_obj(
            content, [vim.Datastore], template.datastore[0].info.name)

    # if None, get the first one
    cluster = get_obj(content, [vim.ClusterComputeResource], cluster_name)

    if resource_pool:
        resource_pool = get_obj(content, [vim.ResourcePool], resource_pool)
    else:
        resource_pool = cluster.resourcePool

    vmconf = vim.vm.ConfigSpec()

    if datastorecluster_name:
        podsel = vim.storageDrs.PodSelectionSpec()
        pod = get_obj(content, [vim.StoragePod], datastorecluster_name)
        podsel.storagePod = pod

        storagespec = vim.storageDrs.StoragePlacementSpec()
        storagespec.podSelectionSpec = podsel
        storagespec.type = 'create'
        storagespec.folder = destfolder
        storagespec.resourcePool = resource_pool
        storagespec.configSpec = vmconf

        try:
            rec = content.storageResourceManager.RecommendDatastores(
                storageSpec=storagespec)
            rec_action = rec.recommendations[0].action[0]
            real_datastore_name = rec_action.destination.name
        except:
            real_datastore_name = template.datastore[0].info.name

        datastore = get_obj(content, [vim.Datastore], real_datastore_name)

    # set relospec
    relospec = vim.vm.RelocateSpec()
    relospec.datastore = datastore
    relospec.pool = resource_pool

    clonespec = vim.vm.CloneSpec()
    clonespec.location = relospec
    clonespec.powerOn = power_on

    # print('=' * 100)
    print("-- Starting to Clone VM --")
    task = template.Clone(folder=destfolder, name=vm_name, spec=clonespec)
    wait_for_task(task)
    print("-- The VM has been Cloned --")


def clone_vm_from_no(vm_no,temp_no):

    si = SmartConnectNoSSL(
         host='172.16.1.200',
         user='administrator@vsphere.local',
         pwd='Cisc0123,,..//',
         port=443)

    atexit.register(Disconnect, si)
    content = si.RetrieveContent()
    template = None

    if temp_no == 1:
        template = get_obj(content, [vim.VirtualMachine], 'vm_temp_cpu1_mem1')

    elif temp_no == 2:
        template = get_obj(content, [vim.VirtualMachine], 'vm_temp_cpu1_mem2')

    elif temp_no == 3:
        template = get_obj(content, [vim.VirtualMachine], 'vm_temp_cpu2_mem1')

    elif temp_no == 4:
        template = get_obj(content, [vim.VirtualMachine], 'vm_temp_cpu2_mem2')

    vm_name = 'CentOS_'+str(vm_no)

    clone_vm(
        content, template, vm_name, si,
        None, 'vm_cloned_from_template',
        None, None, 'QYT_Cloud',
        False, None)

    return None

if __name__ == "__main__":
    clone_vm_from_no(98,1)
