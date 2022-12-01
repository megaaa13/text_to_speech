
# Copyright (C) 2022 yui-mhcp project's author. All rights reserved.
# Licenced under the Affero GPL v3 Licence (the "Licence").
# you may not use this file except in compliance with the License.
# See the "LICENCE" file at the root of the directory for the licence information.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from hparams.hparams import HParams

HParamsTacotron2Encoder = HParams(
    _prefix     = 'encoder',
    
    pad_token   = 0,
    embedding_dim   = 512,
    n_conv  = 3,
    kernel_size     = 5,
    use_bias        = True,
    
    bnorm           = 'after',
    epsilon         = 1e-5,
    momentum        = 0.1,

    drop_rate       = 0.5,
    activation      = 'relu',
    
    n_speaker       = 1,
    speaker_embedding_dim   = None,
    concat_mode         = 'concat',
    linear_projection   = False,
    
    name    = 'encoder'
)

HParamsTacotron2Prenet  = HParams(
    _prefix = 'prenet',
    
    sizes       = [256, 256],
    use_bias    = False,
    activation  = 'relu', 
    drop_rate   = 0.5,
    deterministic   = False,
    name        = 'prenet'
)

HParamsTacotron2Postnet = HParams(
    _prefix     = 'postnet',
    
    n_conv      = 5,
    filters     = 512,
    kernel_size = 5,
    use_bias    = True,
    
    bnorm       = 'after',
    epsilon     = 1e-5,
    momentum    = 0.1,
    
    drop_rate   = 0.5,
    activation  = 'tanh',
    final_activation    = None,
    linear_projection   = False,
    name    = 'postnet'
)

HParamsTacotron2LSA = HParams(
    _prefix     = 'lsa',
    
    attention_dim   = 128,
    attention_filters   = 32,
    attention_kernel_size   = 31,
    probability_function    = 'softmax',
    concat_mode     = 2,
    cumulative      = True,
    name    = 'location_sensitive_attention'
)

HParamsTacotron2Sampler = HParams(
    gate_threshold     = 0.5,
    max_decoder_steps  = 1024,
    early_stopping     = True,
    add_go_frame       = False,
    remove_last_frame  = False,
    
    teacher_forcing_mode    = 'constant',
    init_ratio      = 1.0,
    final_ratio     = 0.75,
    init_decrease_step  = 50000,
    decreasing_steps    = 50000
)

HParamsTacotron2Decoder = HParams(
    n_mel_channels  = 80,
    with_logits     = True,
    n_frames_per_step   = 1,
    pred_stop_on_mel    = False,
    
    attention_rnn_dim  = 1024, 
    p_attention_dropout    = 0.,
        
    decoder_n_lstm     = 1,
    decoder_rnn_dim    = 1024,
    p_decoder_dropout  = 0.
) + HParamsTacotron2Prenet + HParamsTacotron2LSA + HParamsTacotron2Sampler

def HParamsTacotron2(vocab_size = 148, ** kwargs):
    hparams = HParamsTacotron2Encoder + HParamsTacotron2Decoder + HParamsTacotron2Postnet
    return hparams(vocab_size = vocab_size, ** kwargs)
