from py3dbp import Packer, Bin, Item#, Painter
import time
start = time.time()

'''

This example can be used to compare the fix_point function with and without the fix_point function.

'''

# init packing function
packer = Packer()

# packer.add_bin(Bin('Auto', 130,73,62, 100))

# packer.add_item(Item('Kiste', 62, 35, 38, 1, valid_rotations=RotationType.ALL, color=1))
# packer.add_item(Item('PC-Kiste', 51,36,48, 1, valid_rotations=RotationType.FACE_UP, color=2))
# packer.add_item(Item('Wäschekorb', 49,29,27, 1, valid_rotations=RotationType.FACE_UP, color=3))
# packer.add_item(Item('Werkzeugbox', 39,19,18, 1, valid_rotations=RotationType.ALL, color=3))
# packer.add_item(Item('Ikea Tüte', 40,24,18, 1, valid_rotations=RotationType.ALL, color=4))
# Evergreen Real Container (20ft Steel Dry Cargo Container)
# Unit cm/kg
box = Bin(
    partno='example0',
    WHD=( 130,73,62),
    max_weight= 100,
    corner=0,
    put_type=0
)

packer.addBin(box)

# dyson DC34 (20.5 * 11.5 * 32.2 ,1.33kg)
# 64 pcs per case ,  82 * 46 * 170 (85.12)
for i in range(6):
    packer.addItem(Item(
        partno=' {}'.format(str(i+1)),
        name='Kiste', 
        typeof='cube',
        WHD=(62, 35, 38),
        weight=1,
        level=0,
        loadbear=100,
        updown=True,
        color=1)
    )

# washing machine (85 * 60 *60 ,10 kG)
# 1 pcs per case, 85 * 60 *60 (10)
# for i in range(1):
#     packer.addItem(Item(
#         partno='PC-Kiste{}'.format(str(i+1)),
#         name='PC-Kiste',
#         typeof='cube',
#         WHD=(51,36,48), 
#         weight=1,
#         level=1,
#         loadbear=500,
#         updown=True,
#         color='#FFFF37'
#     ))

# 42U standard cabinet (60 * 80 * 200 , 80 kg)
# one per box, 60 * 80 * 200 (80)
# for i in range(45):
#     packer.addItem(Item(
#         partno=' {}'.format(str(i+1)),
#         name='Ikea Tüte ',
#         typeof='cube',
#         WHD=(27,15,12),
#         weight=1,
#         level=0,
#         loadbear=100,
#         updown=True,
#         color='#842B00')
#     )

# # Server (70 * 100 * 30 , 20 kg) 
# # one per box , 70 * 100 * 30 (20)
# for i in range(50):
#     packer.addItem(Item(
#         partno='Server{}'.format(str(i+1)),
#         name='server',
#         typeof='cube',
#         WHD=(70, 100, 30), 
#         weight=20,
#         level=1,
#         loadbear=500,
#         updown=True,
#         color='#0000E3')
#     )


# calculate packing
packer.pack(
    bigger_first=True,
    distribute_items=False,
    fix_point=True, # Try switching fix_point=True/False to compare the results
    check_stable=True,
    support_surface_ratio=0.75,
    number_of_decimals=0
)

# print result
for box in packer.bins:

    volume = box.width * box.height * box.depth
    print(":::::::::::", box.string())

    print("FITTED ITEMS:")
    volume_t = 0
    volume_f = 0
    unfitted_name = ''

    # '''
    for item in box.items:
        print("partno : ",item.partno)
        print("type : ",item.name)
        print("color : ",item.color)
        print("position : ",item.position)
        print("rotation type : ",item.rotation_type)
        print("W*H*D : ",str(item.width) +'*'+ str(item.height) +'*'+ str(item.depth))
        print("volume : ",float(item.width) * float(item.height) * float(item.depth))
        print("weight : ",float(item.weight))
        volume_t += float(item.width) * float(item.height) * float(item.depth)
        print("***************************************************")
    print("***************************************************")
    # '''
    print("UNFITTED ITEMS:")
    for item in box.unfitted_items:
        print("partno : ",item.partno)
        print("type : ",item.name)
        print("color : ",item.color)
        print("W*H*D : ",str(item.width) +'*'+ str(item.height) +'*'+ str(item.depth))
        print("volume : ",float(item.width) * float(item.height) * float(item.depth))
        print("weight : ",float(item.weight))
        volume_f += float(item.width) * float(item.height) * float(item.depth)
        unfitted_name += '{},'.format(item.partno)
        print("***************************************************")
    print("***************************************************")
    print('space utilization : {}%'.format(round(volume_t / float(volume) * 100 ,2)))
    print('residual volumn : ', float(volume) - volume_t )
    print('unpack item : ',unfitted_name)
    print('unpack item volumn : ',volume_f)
    print("gravity distribution : ",box.gravity)
    # '''
    stop = time.time()
    print('used time : ',stop - start)

    # draw results
    print(box)
#     painter = Painter(box)
#     fig = painter.plotBoxAndItems(
#         title=box.partno,
#         alpha=0.2,
#         write_num=True,
#         fontsize=10
#     )
# fig.show()
fig=box._plot()
fig.show()