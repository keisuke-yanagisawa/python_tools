from pathlib import Path
import shutil
import tempfile

import h5py
import numpy as np
from sklearn import metrics
import torch
from tqdm import tqdm


def predict_loader(model, loader, device):
    y_pred = []
    y_true = []
    for X, y in loader:
        X = X.to(device)
        y = y.to(device)
        y_pred.append(model(X))
        y_true.append(y)
    y_pred = torch.cat(y_pred)
    y_true = torch.cat(y_true)

    return y_pred, y_true


class BalancedRankNetWithLogitsLoss(torch.nn.Module):
    def __init__(self):
        super(BalancedRankNetWithLogitsLoss, self).__init__()

    def forward(self, inputs, targets):
        size = (len(inputs)//2) * 2
        inputs_l, inputs_r = inputs[:size//2], inputs[size//2:size]
        targets_l, targets_r = targets[:size//2], targets[size//2:size]

        inputs = inputs_l - inputs_r
        inputs = inputs.sigmoid()

        halves = torch.ones(targets_l.shape) / 2
        targets = torch.where(targets_l == targets_r,
                              halves.cuda(),
                              (targets_l > targets_r).float())
        weight_same = 0.5 / torch.mean((targets_l == targets_r).float())
        weight_diff = 0.5 / torch.mean((targets_l != targets_r).float())
        weights = torch.where(targets_l == targets_r,
                              weight_same,
                              weight_diff)
        return torch.nn.functional.binary_cross_entropy(inputs, targets, weight=weights) \
            - torch.nn.functional.binary_cross_entropy(targets, targets, weight=weights)
        # Second term was added to adjust the best loss to 0
        # It does not effect grads of inputs


class RankNetWithLogitsLoss(torch.nn.Module):
    def __init__(self):
        super(RankNetWithLogitsLoss, self).__init__()

    def forward(self, inputs, targets):
        size = (len(inputs)//2) * 2
        inputs_l, inputs_r = inputs[:size//2], inputs[size//2:size]
        targets_l, targets_r = targets[:size//2], targets[size//2:size]

        inputs = inputs_l - inputs_r
        inputs = inputs.sigmoid()

        halves = torch.ones(targets_l.shape) / 2
        targets = torch.where(targets_l == targets_r,
                              halves.cuda(),
                              (targets_l > targets_r).float())
        return torch.nn.functional.binary_cross_entropy(inputs, targets) \
            - torch.nn.functional.binary_cross_entropy(targets, targets)
        # Second term was added to adjust the best loss to 0
        # It does not effect grads of inputs


class RankNetWithLogitsLossTest(torch.nn.Module):
    def __init__(self):
        super(RankNetWithLogitsLossTest, self).__init__()

    def forward(self, inputs, targets):
        inputs_p, inputs_n = inputs[targets == 1], inputs[targets == 0]
        size = min(len(inputs_p), len(inputs_n))
        if(size == 0):
            return torch.tensor([0.0], required_grad=True).cuda()
        inputs_p, inputs_n = inputs_p[:size], inputs_n[:size]

        inputs = inputs_p - inputs_n
        inputs = inputs.sigmoid()

        targets = torch.ones(size).cuda()
        return torch.nn.functional.binary_cross_entropy(inputs, targets)


def eval_acc_with_sigmoid(inputs, targets):
    inputs = inputs.cpu().detach().numpy()
    targets = targets.cpu().detach().numpy()
    inputs = inputs > 0
    return metrics.accuracy_score(targets, inputs)


def eval_auroc_with_sigmoid(inputs, targets):
    inputs = inputs.cpu().detach().numpy()
    targets = targets.cpu().detach().numpy()

    if np.sum(targets) == targets[0]:
        return 1.0  # impossible to calc AUROC if the all labels are same

    return metrics.roc_auc_score(targets, inputs)


def __calculate(model, loss_fn, eval_fn, loader, device, opt=None):
    """
    evaluation mode if opt==None
    training mode if opt!=None
    """
    if opt is None:
        model.eval()

    y_pred = []
    y_true = []
    losses = []

    with tqdm(loader) as pbar:
        for batch_idx, (X, y) in enumerate(pbar):

            X, y = X.to(device), y.to(device)
            y_pred.append(model(X))
            y_true.append(y)

            eval_value = eval_fn(y_pred[-1], y_true[-1])

            loss = loss_fn(y_pred[-1], y_true[-1])
            losses.append(loss.cpu().detach().numpy())

            if not opt is None:
                opt.zero_grad()
                loss.backward()
                opt.step()
            else:
                # release calculation graph
                y_pred[-1] = y_pred[-1].detach()
                y_true[-1] = y_true[-1].detach()

            pbar.set_postfix({
                "loss": round(losses[-1].mean(), 3),
                "eval_value": round(eval_value, 3),
                "example": round(y_pred[-1].cpu().detach().numpy().reshape(-1)[0], 2),
            })

    if opt is None:
        model.train()

    return np.mean(losses), eval_fn(torch.cat(y_pred), torch.cat(y_true))


def train(model, loss_fn, opt, train_loader, valid_loader, device, nEpoch=50,
          lr_scheduler=None):
    # file initialization
    with open("test.csv", "w") as fout:
        fout.write("epoch,loss,accuracy,val_loss,val_accuracy\n")

    for epoch in range(nEpoch):
        train_loss, train_accuracy = __calculate(
            model, loss_fn, eval_auroc_with_sigmoid, train_loader, device, opt=opt)
        valid_loss, valid_accuracy = __calculate(
            model, loss_fn, eval_auroc_with_sigmoid, valid_loader, device)

        if lr_scheduler is not None:
            lr_scheduler.step()

        with open("test.csv", "a") as fout:
            fout.write(f"{epoch}, {train_loss}, {train_accuracy}, {valid_loss}, {valid_accuracy}\n")

    return model


_rotation_list = [
    (0, 0, 0), (0, 0, 1), (0, 0, 2), (0, 0, 3),
    (0, 1, 0), (0, 1, 1), (0, 1, 2), (0, 1, 3),
    (0, 2, 0), (0, 2, 1), (0, 2, 2), (0, 2, 3),
    (0, 3, 0), (0, 3, 1), (0, 3, 2), (0, 3, 3),
    (1, 1, 0), (1, 1, 1), (1, 1, 2), (1, 1, 3),
    (1, 3, 0), (1, 3, 1), (1, 3, 2), (1, 3, 3),
]


def voxel_rotation(voxel, index=0):
    assert(0 <= index and index < len(_rotation_list))
    rot = _rotation_list[index]
    ret = np.rot90(voxel, rot[0], (0, 1))
    ret = np.rot90(ret, rot[1], (1, 2))
    ret = np.rot90(ret, rot[2], (0, 1))
    return ret


class MyDataset(torch.utils.data.Dataset):
    def _filepath(self, prefix):
        return self.DATA_DIR / prefix

    def _init_temp_dir(self):
        return Path(tempfile.mkdtemp())

    def _temp_filepath(self, prefix):
        path = self.temp_dir / prefix
        if not path.exists():
            src = self._filepath(prefix)
            dst = path
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(src, dst)
        return path

    def _load_data(self, prefix_idx, idx_in_file):
        prefix_idx = int(prefix_idx)
        prefix = self.prefixes[prefix_idx]
        # if(idx_in_file == '1335' or idx_in_file == '3251'):
        #    print(prefix, prefix_idx, idx_in_file)

        with h5py.File(self._temp_filepath(prefix+".X.h5"), "r") as h5file:
            # print(h5file.keys())
            X = h5file[idx_in_file][:]

        with h5py.File(self._temp_filepath(prefix+".y.h5"), "r") as h5file:
            # print("'",idx_in_file,"'")
            idx = np.where(h5file["resn"][:] == idx_in_file)[0]
            y = h5file["label"][idx]
            # print("y", y)
            # print("idx_in_file", idx_in_file)
            # print("y[0]", y[0])
            # print("type(idx_in_file)", type(idx_in_file))
            # print("y[idx_in_file]", y[idx_in_file])
        return X, y

    def get_labels(self):
        # True/False are saved as String (weildly...)
        return self.shuffle_list[:, -1] == "True"

    def _data_list_shuffle(self):
        len_pos = len(self.positive_list)
        len_neg = len(self.negative_list)
        if self.balanced:
            len_smaller = np.min([len_pos, len_neg])
            pos_indices = np.random.choice(len_pos, len_smaller)
            neg_indices = np.random.choice(len_neg, len_smaller)
        else:
            pos_indices = np.arange(len_pos)
            neg_indices = np.arange(len_neg)

        self.shuffle_list = np.vstack([
            np.hstack([self.positive_list[pos_indices],
                       np.repeat(True, len(pos_indices)).reshape(-1, 1)]),
            np.hstack([self.negative_list[neg_indices],
                       np.repeat(False, len(neg_indices)).reshape(-1, 1)])
        ])
        np.random.shuffle(self.shuffle_list)
        # print(self.shuffle_list)

    def _data_augmentation(self):
        new_positive_list = []
        for i, info in enumerate(self.positive_list):
            count = int(self.positive_sampling_ratio*(i+1)) - int(self.positive_sampling_ratio*i)
            if count == 0:
                continue
            rot_indices = np.random.choice(len(_rotation_list), count)
            for rot_index in rot_indices:
                new_positive_list.append((*info, rot_index))
        self.positive_list = np.array(new_positive_list)

        new_negative_list = []
        for i, info in enumerate(self.negative_list):
            count = int(self.negative_sampling_ratio*(i+1)) - int(self.negative_sampling_ratio*i)
            if count == 0:
                continue
            rot_indices = np.random.choice(len(_rotation_list), count)
            for rot_index in rot_indices:
                new_negative_list.append((*info, rot_index))
        self.negative_list = np.array(new_negative_list)

    def _data_init(self):
        for prefix_idx, prefix in tqdm(enumerate(self.prefixes)):
            with h5py.File(self._temp_filepath(prefix+".X.h5"), "r") as h5file:
                xkeys = np.array(list(h5file.keys()))
            with h5py.File(self._temp_filepath(prefix+".y.h5"), "r") as h5file:
                ykeys = h5file["resn"][:]
                labels = h5file["label"][:]

            keys = set(xkeys) & set(ykeys)
            ykeys_indices = np.where([(key in keys) for key in ykeys])[0]
            # print(ykeys_indices)
            for idx in ykeys_indices:
                if labels[idx]:
                    self.positive_list.append((prefix_idx, ykeys[idx]))
                else:
                    self.negative_list.append((prefix_idx, ykeys[idx]))
        print(len(self.positive_list), len(self.negative_list))

        self._data_augmentation()
        self._data_list_shuffle()

    def __init__(self, prefixes, DATA_DIR,
                 positive_sampling_ratio=1.0,
                 negative_sampling_ratio=1.0,
                 use_tempdir=False,
                 balanced=False):

        self.prefixes = prefixes
        self.use_tempdir = use_tempdir
        self.DATA_DIR = Path(DATA_DIR)
        self.balanced = balanced
        if self.use_tempdir:
            self.temp_dir = self._init_temp_dir()
        else:
            self.temp_dir = self.DATA_DIR

        self.positive_sampling_ratio = min(positive_sampling_ratio, 24)
        self.negative_sampling_ratio = min(negative_sampling_ratio, 24)
        self.positive_list = []
        self.negative_list = []
        self.shuffle_list = []
        self._data_init()

        self.log = []

    def __len__(self):
        return len(self.shuffle_list)

    def __getitem__(self, idx):
        aData = self.shuffle_list[idx]
        temp = self._load_data(*aData[:2])
        X = voxel_rotation(temp[0], int(aData[2]))
        y = temp[1]
        return torch.from_numpy(X.copy().transpose((3, 0, 1, 2))), torch.tensor(y, dtype=torch.float)

    def delete_temp(self):
        if self.use_tempdir:
            print("remove temp directory {}".format(self.temp_dir))
            shutil.rmtree(self.temp_dir)
        else:
            print("WARNING: have not used tempdir")

    def on_epoch_end(self):
        self._data_list_shuffle()

    def class_weight(self):
        adict = dict(self.data_count)
        maximum = max(adict.values())
        for key in adict.keys():
            adict[key] = maximum / adict[key]
        # print(adict)
        return adict
