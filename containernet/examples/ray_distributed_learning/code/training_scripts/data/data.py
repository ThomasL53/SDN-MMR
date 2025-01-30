import argparse

import torch
from torchvision import datasets, transforms
from torchvision.transforms import ToTensor
from torch.utils.data import SubsetRandomSampler, Subset

dataset_classes = {
    "mnist": {
        "class": datasets.MNIST,
        "num_classes": 10,
        "shape": (1, 1, 28, 28),
        "transforms": {
            "train": transforms.Compose(
                [transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))]
            ),
            "test": transforms.Compose(
                [transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))]
            ),
        },
    },
    "fashion_mnist": {
        "class": datasets.FashionMNIST,
        "num_classes": 10,
        "shape": (1, 1, 28, 28),
        "transforms": {
            "train": ToTensor(),
            "test": ToTensor(),
        },
    },
    "cifar100": {
        "class": datasets.CIFAR100,
        "num_classes": 100,
        "shape": (1, 3, 32, 32),
        "transforms": {
            "train": transforms.Compose(
                [
                    transforms.RandomCrop(32, padding=4),
                    transforms.RandomHorizontalFlip(),
                    transforms.ToTensor(),
                    transforms.Normalize(
                        (0.5071, 0.4867, 0.4408), (0.2675, 0.2565, 0.2761)
                    ),
                ]
            ),
            "test": transforms.Compose(
                [
                    transforms.ToTensor(),
                    transforms.Normalize(
                        (0.5071, 0.4867, 0.4408), (0.2675, 0.2565, 0.2761)
                    ),
                ]
            ),
        },
    },
}


def get_classes_and_shape(dataset_name: str):
    return (
        dataset_classes[dataset_name]["num_classes"],
        dataset_classes[dataset_name]["shape"],
    )


def get_train_dataset(dataset_name: str, data_dir: str = "~/data"):
    dataset_info = dataset_classes[dataset_name]
    dataset_class = dataset_info["class"]

    return dataset_class(
        data_dir,
        train=True,
        download=True,
        transform=dataset_info["transforms"]["train"],
    )


def get_test_dataset(dataset_name: str, data_dir: str = "~/data"):
    dataset_info = dataset_classes[dataset_name]
    dataset_class = dataset_info["class"]

    return dataset_class(
        data_dir,
        train=False,
        download=True,
        transform=dataset_info["transforms"]["test"],
    )


def get_train_loader(
    dataset: str,
    batch_size: int = 64,
    shuffle_data: bool = True,
    data_dir="~/data",
    num_workers: int = 1,
    worker_rank: int = 0,
):
    train_dataset = get_train_dataset(dataset, data_dir)
    # Calculate the range of indices for each worker
    dataset_size = len(train_dataset)
    indices = list(range(dataset_size))

    # This partitioning of the dataset may lead to some data not being used
    # (up to num_workers - 1 samples) as each worker receives exactly the same
    # amount. This is required, as ps_async expects all workers to have the same
    # amount when calculating the number of iterations.
    worker_data_size = dataset_size // num_workers
    worker_start_idx = worker_rank * worker_data_size
    worker_end_idx = (worker_rank + 1) * worker_data_size
    assert worker_end_idx <= dataset_size

    # Create a SubsetRandomSampler or Subset
    train_sampler = (
        SubsetRandomSampler(indices[worker_start_idx:worker_end_idx])
        if shuffle_data
        else Subset(train_dataset, indices[worker_start_idx:worker_end_idx])
    )

    train_loader = torch.utils.data.DataLoader(
        train_dataset, batch_size=batch_size, sampler=train_sampler
    )

    return train_loader


def get_test_loader(dataset: str, batch_size: int = 64, data_dir="~/data"):
    test_dataset = get_test_dataset(dataset, data_dir)
    test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=batch_size)
    return test_loader


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data",
        type=str,
        required=True,
        choices=list(dataset_classes.keys()) + ["all"],
        help="Specify dataset to download.",
    )

    args, _ = parser.parse_known_args()

    if args.data == "all":
        datasets_to_download = dataset_classes.keys()
    else:
        datasets_to_download = [args.data]

    for dataset_name in datasets_to_download:
        get_train_dataset(dataset_name)
        get_test_dataset(dataset_name)
