
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

import tensorflow as tf

from utils.embeddings import compute_centroids
from utils.distance.distance_method import tf_distance
from utils.distance.clustering import clustering_wrapper, get_assignment, compute_score

@tf.function(reduce_retracing = True, experimental_follow_type_hints = True)
def _kmeans(points  : tf.Tensor,
            k       : tf.Tensor,

            n_init       = 5,
            max_iter    : tf.Tensor = 100,
            threshold   : tf.Tensor = 1e-6,
            init_method = 'kmeans_pp',
            distance_metric = 'euclidian',
            random_state    = None
           ):
    if n_init > 1:
        best_centroids  = tf.zeros((k, tf.shape(points)[1]), tf.float32)
        best_assignment = tf.range(tf.shape(points)[0])
        best_score      = -1.
        for run in tf.range(n_init):
            centroids, assignment = _kmeans(
                points,
                k,
                n_init  = 0,
                init_method = init_method,
                max_iter    = max_iter,
                threshold   = threshold,
                distance_metric = distance_metric
            )
            centroids.set_shape(best_centroids.shape)
            assignment.set_shape(best_assignment.shape)
            
            score = compute_score(
                points, assignment, centroids, tf.range(k, dtype = tf.int32), distance_metric = distance_metric
            )

            if score < best_score or best_score == -1.:
                best_score, best_centroids, best_assignment = score, centroids, assignment
        
        return best_centroids, best_assignment
    
    if init_method == 'normal':
        centroids = tf.random.normal(
            (k, tf.shape(points)[1]), seed = random_state
        )
    elif init_method == 'uniform':
        centroids = tf.random.uniform(
            shape   = (k, tf.shape(points)[1]),
            minval  = tf.reduce_min(points),
            maxval  = tf.reduce_max(points),
            seed    = random_state
        )
    elif init_method == 'random':
        indexes = tf.random.shuffle(tf.range(tf.shape(points)[0]))[:k]
        
        centroids = tf.gather(points, indexes)
    elif init_method == 'kmeans_pp':
        centroids = kmeans_pp_init(
            points, k, distance_metric = distance_metric, random_state = random_state
        )
    else:
        raise ValueError("Initialization mode unknown : {}".format(init_method))
    
    assignment = get_assignment(points, centroids, distance_metric = distance_metric)
    for i in tf.range(max_iter):
        new_centroid_ids, new_centroids = compute_centroids(points, assignment)
        
        if tf.shape(new_centroids)[0] < k:
            unused  = tf.range(k)
            mask    = tf.reduce_all(tf.expand_dims(unused, axis = 1) != new_centroid_ids, axis = 1)
            unused  = tf.boolean_mask(unused, mask)
            
            new_centroids = tf.concat([
                new_centroids, tf.gather(centroids, unused, batch_dims = 0)
            ], axis = 0)
            new_centroid_ids    = tf.concat([new_centroid_ids, unused], axis = 0)
        
        new_centroids = tf.gather(
            new_centroids, tf.argsort(new_centroid_ids), batch_dims = 0
        )
        new_centroids.set_shape(centroids.shape)
        
        if tf.reduce_sum(tf.abs(new_centroids - centroids)) < threshold:
            break
        
        centroids   = new_centroids
        assignment  = get_assignment(points, centroids, distance_metric = distance_metric)
    
    return centroids, assignment

@tf.function(reduce_retracing = True, experimental_follow_type_hints = True)
def kmeans_pp_init(points   : tf.Tensor,
                   k        : tf.Tensor,
                   distance_metric  = 'euclidian',
                   random_state     = None
                  ):
    n   = tf.shape(points)[0]
    idx = tf.random.uniform((), minval = 0, maxval = n, dtype = tf.int32)
    
    centroids = tf.TensorArray(dtype = tf.float32, size = k, dynamic_size = False)
    centroids = centroids.write(0, tf.gather(points, idx))
    
    for i in tf.range(1, k):
        dist = tf.reduce_min(tf_distance(
            points, centroids.stack()[:i], distance_metric, as_matrix = True, force_distance = True
        ), axis = -1)

        centroids = centroids.write(
            i, tf.gather(points, tf.argmax(dist, axis = -1))
        )
    
    return centroids.stack()

kmeans = clustering_wrapper(_kmeans)