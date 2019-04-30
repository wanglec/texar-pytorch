# Copyright 2018 The Texar Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Various utilities for losses.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


import torch

from texar.utils.shapes import mask_sequences

# pylint: disable=invalid-name, not-context-manager, protected-access,
# pylint: disable=too-many-arguments

__all__ = [
    "mask_and_reduce",
    "reduce_batch_time",
    "reduce_dimensions"
]


def mask_and_reduce(sequence,
                    sequence_length,
                    rank=2,
                    average_across_batch=True,
                    average_across_timesteps=False,
                    average_across_remaining=False,
                    sum_over_batch=False,
                    sum_over_timesteps=True,
                    sum_over_remaining=True,
                    dtype=None,
                    time_major=False):
    """Masks out sequence entries that are beyond the respective sequence
    lengths, and reduces (average or sum) away dimensions.

    This is a combination of :func:`~texar.utils.shapes.mask_sequences`
    and :func:`~texar.losses.losses_utils.reduce_batch_time`.

    Args:
        sequence: A Tensor of sequence values.
            If `time_major=False` (default), this must be a Tensor of shape
            `[batch_size, max_time, d_2, ..., d_rank]`, where the rank of
            the Tensor is specified with :attr:`rank`.
            The batch and time dimensions are exchanged if `time_major` is True.
        sequence_length: A Tensor of shape `[batch_size]`. Time steps beyond
            the respective sequence lengths will be made zero. If `None`,
            not masking is performed.
        rank (int): The rank of :attr:`sequence`. Must be >= 2. Default is 2,
            i.e., `sequence` is a 2D Tensor consisting of batch and time
            dimensions.
        average_across_timesteps (bool): If set, average the sequence across
            the time dimension. Must not set `average_across_timesteps`
            and `sum_over_timesteps` at the same time.
        average_across_batch (bool): If set, average the sequence across the
            batch dimension. Must not set `average_across_batch`'
            and `sum_over_batch` at the same time.
        average_across_remaining (bool): If set, average the sequence across the
            remaining dimensions. Must not set `average_across_remaining`'
            and `sum_over_remaining` at the same time.
        sum_over_timesteps (bool): If set, sum the loss across the
            time dimension. Must not set `average_across_timesteps`
            and `sum_over_timesteps` at the same time.
        sum_over_batch (bool): If set, sum the loss across the
            batch dimension. Must not set `average_across_batch`
            and `sum_over_batch` at the same time.
        sum_over_remaining (bool): If set, sum the loss across the
            remaining dimension. Must not set `average_across_remaining`
            and `sum_over_remaining` at the same time.
        time_major (bool): The shape format of the inputs. If `True`,
            :attr:`sequence` must have shape `[max_time, batch_size, ...]`.
            If `False` (default), `sequence` must have
            shape `[batch_size, max_time, ...]`.
        dtype (dtype): Type of :attr:`sequence`. If `None`, infer from
            :attr:`sequence` automatically.

    Returns
        A Tensor containing the masked and reduced sequence.
    """




def reduce_batch_time(sequence,
                      sequence_length,
                      average_across_batch=True,
                      average_across_timesteps=False,
                      sum_over_batch=False,
                      sum_over_timesteps=True):
    """Average or sum over the respective dimensions of :attr:`sequence`, which
    is of shape `[batch_size, max_time, ...]`.

    Assumes :attr:`sequence` has been properly masked according to
    :attr:`sequence_length`.
    """
    if average_across_timesteps and sum_over_timesteps:
        raise ValueError("Only one of `average_across_timesteps` and "
                         "`sum_over_timesteps` can be set.")
    if average_across_batch and sum_over_batch:
        raise ValueError("Only one of `average_across_batch` and "
                         "`sum_over_batch` can be set.")

    if sum_over_timesteps:
        sequence = torch.sum(sequence, dim=1)
    elif average_across_timesteps:
        if sequence_length is None:
            sequence = torch.mean(sequence, dim=1)
        else:
            sequence = torch.sum(sequence, dim=1).float() / \
                       sequence_length.float()

    if sum_over_batch:
        sequence = torch.sum(sequence, dim=0)
    elif average_across_batch:
        sequence = torch.mean(sequence, dim=0)

    return sequence


def reduce_dimensions(tensor, average_axes=None, sum_axes=None, keepdims=None):
    """Average or sum over dimensions of :attr:`tensor`.

    :attr:`average_axes` and :attr:`sum_axes` must be mutually exclusive. That
    is, elements in `average_axes` must not be contained in
    `sum_axes`, and vice versa.

    Args:
        tensor: A tensor to reduce.
        average_axes (optional): A (list of) `int` that indicates the
            dimensions to reduce by taking average.
        sum_axes (optional): A (list of) `int` that indicates the
            dimensions to reduce by taking sum.
        keepdims (optional): If `True`, retains reduced dimensions with
            length 1.
    """
    reduced_axes = set()
    if average_axes is not None:
        if not isinstance(average_axes, (list, tuple)):
            average_axes = [average_axes]
        if len(average_axes) > 0:
            for average_axis in average_axes:
                tensor = torch.mean(tensor, dim=average_axis, keepdim=True)
            reduced_axes.update(average_axes)

    if sum_axes is not None:
        if not isinstance(sum_axes, (list, tuple)):
            sum_axes = [sum_axes]
        if len(sum_axes) > 0:
            for sum_axis in sum_axes:
                tensor = torch.sum(tensor, dim=sum_axis, keepdim=True)
            reduced_axes.update(sum_axes)

            if average_axes is not None:
                if len(reduced_axes) != len(average_axes) + len(sum_axes):
                    raise ValueError('`average_axes` and `sum_axes` must not '
                                     'have overlapped elements.')
    if not keepdims:
        tensor = torch.squeeze(tensor, dim=list(reduced_axes))

    return tensor




