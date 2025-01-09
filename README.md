# AX88179A Macos Fix

The [ASIX AX88179](https://www.asix.com.tw/en/product/USBEthernet/Super-Speed_USB_Ethernet/AX88179) chip is ubiquitous in USB NICs. I had trouble using them with both macos and opnsense. As I was looking for a solution for opnsense, I found [this comment](https://forum.opnsense.org/index.php?msg=174987), which solved it for me there (it seems fine since implementing that solution). But there isn't an immediate substitute for usbconfig in macos, so I developed this small python script.
It should work with other devices that need set_config=1, too.
