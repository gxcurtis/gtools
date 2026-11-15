# Snappy
common:
    -snapshot name
    
    
Create:
```sh
virsh snapshot-create-as <VM> <SNAPSHOTNAME> --disk-only
```

Commit:
```sh
virsh blockcommit <VM> --snapshotname <SNAPSHOTNAME> --pivot
```

Revert:
```sh
virsh destroy <VM>
virsh dumpxml <VM> | tee file
(Process xml)
virsh define <XML_FILE> 
```

Command drafting:

- snappy -s snap create vm-name
- snappy -s snap commit vm-name
- snappy -s snap revert vm-name

