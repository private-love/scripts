def iplist():
    iplist_dict = {"publicnetwork": ["192.168.0.238:29622",
                                    "192.168.0.65:22"
                                     ],
                   "192.168.0.238:29622": ["192.168.3.217:22",
                                          "192.168.0.14:22"
                                           ]
                   }
    return iplist_dict
iplist_dict = iplist()