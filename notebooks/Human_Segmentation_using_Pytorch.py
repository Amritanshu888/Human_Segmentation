#!/usr/bin/env python
# coding: utf-8

# ### 1. Import libraries

# In[1]:


import torch 
import cv2

import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt 

from tqdm import tqdm
import albumentations as A
from torch.utils.data import Dataset,DataLoader
from sklearn.model_selection import train_test_split
from torch import nn
import segmentation_models_pytorch as smp
from segmentation_models_pytorch.losses import DiceLoss


# ### 2. Check Pytorch Cuda Version

# In[2]:


print(torch.__version__)

print(torch.version.cuda)


# ### 3. Load Pandas Train CSV File

# In[3]:


file_path = './data/train.csv'
df = pd.read_csv(file_path)


# ### 4. Check top 5 rows of columns

# In[4]:


df.head()


# ### 5. Preparing Masks and Images for Visulaization

# In[5]:


row = df.iloc[8]
image_path = row.images
mask_path = row.masks
image = cv2.imread(image_path)
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE) /255.0


# ### 6. Visualize Mask and Image

# In[6]:


f, (ax1, ax2) = plt.subplots(1, 2, figsize=(10,5))
        
ax1.set_title('IMAGE')
ax1.imshow(image)

ax2.set_title('GROUND TRUTH')
ax2.imshow(mask,cmap = 'gray')


# ### 7. Use Albumentations Library for data augmentation

# In[7]:


def get_train_augs():
  return A.Compose([
                    A.Resize(IMAGE_SIZE, IMAGE_SIZE),
                    A.HorizontalFlip(p = 0.5),
                    A.VerticalFlip(p = 0.5),
                    A.ShiftScaleRotate(shift_limit=0.2, scale_limit=0.2, rotate_limit=30, p=0.5),
                    A.RGBShift(r_shift_limit=25, g_shift_limit=25, b_shift_limit=25, p=0.5),
                    A.RandomBrightnessContrast(brightness_limit=0.3, contrast_limit=0.3, p=0.5)
  ])

def get_valid_augs():
  return A.Compose([
                    A.Resize(IMAGE_SIZE, IMAGE_SIZE)
  ])


# - RGBShift = This can be useful for introducing color variations in the training data to make the model more robust to different lighting conditions.

# ### 8. Prepare Our Custom Data

# In[8]:


class CustomData(Dataset):
    def __init__(self,df, augmentations):
        self.df = df
        self.augmentations = augmentations
    
    def __len__(self):
        return len(self.df)
    
    def __getitem__(self,idx):
        row = self.df.iloc[idx]
        image_path = row.images
        mask_path = row.masks
        
        image = cv2.imread(image_path) # BGR
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE) # this have 2 dim (h,w)
        # we need add new dim (h, w, c)
        mask = np.expand_dims(mask, axis= -1)
        
        if self.augmentations:
            data = self.augmentations(image = image, mask = mask)
            image = data['image']
            mask = data['mask']
            
        #(h, w, c) -> (c, h, w)
        image = np.transpose(image, (2, 0, 1)).astype(np.float32)
        mask = np.transpose(mask, (2, 0, 1)).astype(np.float32)
        
        # convert from np to tensor
        image = torch.Tensor(image) / 255.0
        mask = torch.round(torch.Tensor(mask) / 255.0)
        
        return image, mask


# - `cv2.COLOR_BGR2RGB` -This conversion is important because many other image processing libraries and applications use the RGB color space as the default, so converting an image from BGR to RGB can make it easier to work with

# ### 9. Spliting Data into Train and Test

# In[9]:


IMAGE_SIZE = 320
BATCH_SIZE = 16
train_df, valid_df = train_test_split(df, test_size = 0.2, random_state = 42)


# In[10]:


trainset = CustomData(train_df, get_train_augs())
validset = CustomData(valid_df, get_valid_augs())


# In[11]:


print(f"Size of Trainset : {len(trainset)}")
print(f"Size of Validset : {len(validset)}")


# ### 10. Validating Trainset 

# In[12]:


image, mask  = trainset[4]
f, (ax1, ax2) = plt.subplots(1, 2, figsize=(10,5))
        
ax1.set_title('IMAGE')
ax1.imshow(image.permute(1,2,0))

ax2.set_title('GROUND TRUTH')
ax2.imshow(mask.permute(1,2,0),cmap = 'gray')


# ### 11. Load the dataset folders into a data loader

# In[13]:


trainloader = DataLoader(trainset, batch_size= BATCH_SIZE, shuffle= True)
validloader = DataLoader(validset, batch_size = BATCH_SIZE)


# In[14]:


print(f"Total no. of batches in trainloader : {len(trainloader)}")
print(f"Total no. of batches in validloader : {len(validloader)}")


# In[15]:


for image, mask in trainloader:
  break

print(f"One batch image shape : {image.shape}")
print(f"One batch mask shape : {mask.shape}")
# the second value is no. of channel 


# ### 12. Create Model

# In[16]:


ENCODER = 'timm-efficientnet-b0'
WIEGHTS = 'imagenet'


# In[17]:


class SegmentationModel(nn.Module):

  def __init__(self):
      super(SegmentationModel, self).__init__()

      self.arc = smp.Unet(
          encoder_name= ENCODER,
          encoder_weights= WIEGHTS,
          in_channels= 3,
          classes= 1,
          activation= None
      )
  def forward(self, images, masks = None):

    logits = self.arc(images)

    if masks != None:
      loss1 = DiceLoss(mode= 'binary')(logits, masks)
      loss2 = nn.BCEWithLogitsLoss()(logits, masks)
      return logits, loss1 + loss2

    return logits


# In[18]:


def get_default_device():
    """Pick GPU if available, else CPU"""
    if torch.cuda.is_available():
        return torch.device('cuda')
    else:
        return torch.device('cpu')


# In[19]:


device = get_default_device()
device


# In[20]:


model = SegmentationModel()
model.to(device)


# ### 13. Prepare Train Function

# In[21]:


def train_function(data_loader, model, optimizer):

  model.train()
  total_loss = 0.0

  for images, masks in tqdm(data_loader):

    images = images.to(device)
    masks = masks.to(device)

    optimizer.zero_grad()
    logits, loss = model(images, masks)
    loss.backward()
    optimizer.step()

    total_loss += loss.item()

  return total_loss / len(data_loader)


# ### 14. Prepare Evaluate Function

# In[22]:


def eval_function(data_loader, model):

  model.eval()
  total_loss = 0.0

  with torch.no_grad():
    for images, masks in tqdm(data_loader):

      images = images.to(device)
      masks = masks.to(device)

      logits, loss = model(images, masks)

      total_loss += loss.item()

  return total_loss / len(data_loader)


# ### 15. Define Hyper Parameters

# In[24]:


EPOCHS = 25
LR = 0.003
optimizer = torch.optim.Adam(model.parameters(), lr= LR)


# ### 16. Train the Model and Save Model

# In[25]:


from pandas.core.algorithms import mode
best_valid_loss = np.Inf

for i in range(EPOCHS):

  train_loss = train_function(trainloader, model, optimizer)
  valid_loss = eval_function(validloader, model)

  if valid_loss < best_valid_loss:
    torch.save(model.state_dict(), 'best_model.pt')
    print("saved model")
    best_valid_loss = valid_loss

  print(f"Epoch : {i+1} Train_loss : {train_loss} valid_loss : {valid_loss}")


# ### 17. Perform predictions

# In[28]:


idx = 50

model.load_state_dict(torch.load('./best_model.pt'))
image, mask = validset[idx]
#used to add an extra dimension for batch as model takes (batch, channel, height, width)
logits_mask = model(image.to(device).unsqueeze(0)) # (C, H, W) -> (1, C, H, W)
pred_mask = torch.sigmoid(logits_mask)
pred_mask = (pred_mask > 0.5) * 1.0


# - Applies a threshold of 0.5 to the probability mask to convert it to a binary mask. 
# - If the probability of a pixel being part of the object is greater than 0.5, it is classified as part of the object and assigned a value of 1.0. Otherwise, it is classified as background and assigned a value of 0.0.

# In[30]:


f, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(10,5))
        
ax1.set_title('IMAGE')
ax1.imshow(image.permute(1,2,0))

ax2.set_title('GROUND TRUTH')
ax2.imshow(mask.permute(1,2,0),cmap = 'gray')
print("MASK",mask.shape)

ax3.set_title('PREDICTION')
ax3.imshow(pred_mask.detach().cpu().squeeze(0).permute(1,2,0))
print("pred_mask",pred_mask.shape)


# In[ ]:




