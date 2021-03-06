# ==============================================================================
# Copyright 2020 The LatticeX Foundation
# This file is part of the Rosetta library.
#
# The Rosetta library is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The Rosetta library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with the Rosetta library. If not, see <http://www.gnu.org/licenses/>.
# =============================================================================="

import tensorflow as tf
import sys
import numpy as np
np.set_printoptions(suppress=True)

import logging
# We can set this level to see more inner info
logging.basicConfig(level=logging.DEBUG)

TEST_CASES = []
######### 1, We get the expected result with the native OP 
#### 1.1 first case: variable / variable
val_a = np.array(
    [
        [2000.0, 20000.0],
        [20000 * 100.0, -200.0]
    ], dtype =np.float)

val_b = np.array(
    [
        [50000, -50000.0],
        [-50000, -0.02] 
    ],dtype= np.float)

curr_case = {}
curr_case["input"] = [val_a, val_b]

var_a = tf.Variable(val_a)
var_b = tf.Variable(val_b)
var_c = var_a / var_b

init = tf.compat.v1.global_variables_initializer() 
with tf.compat.v1.Session() as tf_sess:
    tf_sess.run(init)
    tf_res = tf_sess.run(var_c)
    curr_case["native_res"] = np.array(tf_res, dtype=np.float)

TEST_CASES.append(curr_case)

#### 1.2 second case: constant / variable
curr_case = {}
curr_case["input"] = [val_a, val_b]

const_a = tf.constant(val_a)
var_b = tf.Variable(val_b)
var_c = const_a / var_b

init = tf.compat.v1.global_variables_initializer() 
with tf.compat.v1.Session() as tf_sess:
    tf_sess.run(init)
    tf_res = tf_sess.run(var_c)
    curr_case["native_res"] = np.array(tf_res, dtype=np.float)

TEST_CASES.append(curr_case)

######### 2. We perform the same functionality one by one with Rosetta
import latticex.rosetta as rtt
# all logs will be printed
rtt.py_protocol_handler.set_loglevel(0)
# rtt.activate("Helix")
rtt.activate("SecureNN")

#### 2.1 first case
case_id = 0
rtt_case = TEST_CASES[case_id]

cipher_var_a = tf.Variable(rtt.private_input(0, rtt_case["input"][0]))
cipher_var_b = tf.Variable(rtt.private_input(1, rtt_case["input"][1]))
cipher_var_c = cipher_var_a / cipher_var_b

init = tf.compat.v1.global_variables_initializer() 
with tf.compat.v1.Session() as rtt_sess:
    rtt_sess.run(init)
    rtt_res = rtt_sess.run(cipher_var_c)
    # print("local cipher res:", rtt_res)
    # reveal to get the plaintext result
    rtt_res = rtt_sess.run(rtt.SecureReveal(rtt_res))
    rtt_case["rtt_res"] = np.array(rtt_res, dtype=np.float)

#### 2.2 second case
case_id += 1
rtt_case = TEST_CASES[case_id]

cipher_const_a = tf.constant(rtt_case["input"][0])
cipher_var_b = tf.Variable(rtt.private_input(1, rtt_case["input"][1]))
cipher_var_c = cipher_const_a / cipher_var_b

init = tf.compat.v1.global_variables_initializer() 
with tf.compat.v1.Session() as rtt_sess:
    rtt_sess.run(init)
    rtt_res = rtt_sess.run(cipher_var_c)
    # print("local cipher res:", rtt_res)
    # reveal to get the plaintext result
    rtt_res = rtt_sess.run(rtt.SecureReveal(rtt_res))
    rtt_case["rtt_res"] = np.array(rtt_res, dtype=np.float)

######### 3. We check all the result are correct, with tolerence on precision 
for i in range(len(TEST_CASES)): 
    curr_case = TEST_CASES[i]
    try:
        np.testing.assert_allclose(curr_case["native_res"], curr_case["rtt_res"], rtol=1e-3, atol=0)
        print("{}-th case passed!".format(i))
        print(curr_case)
    
    except Exception as e:
        print("{}-th case failed! And detailed context: {}".format(i, curr_case))

print("*" * 69)



