"""Offline batch validation. Never imported by the web application.

Run `python -m code_practice.build_import_batch` to reproduce all reviewed batches,
or use --ids to validate a specific group without repeating completed work.
"""
from __future__ import annotations

from collections import Counter
import argparse
import ast
import hashlib
import inspect
import json
import multiprocessing
from pathlib import Path
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from .import_batch_001 import BATCH as BATCH_001
from .import_batch_002 import BATCH as BATCH_002
from .import_batch_003 import BATCH as BATCH_003
from .import_batch_004 import BATCH as BATCH_004
from .import_batch_005 import BATCH as BATCH_005
from .import_batch_006 import BATCH as BATCH_006
from .import_batch_007 import BATCH as BATCH_007
from .import_batch_008 import BATCH as BATCH_008
from .import_batch_009 import BATCH as BATCH_009
from .import_batch_010 import BATCH as BATCH_010
from .import_batch_011 import BATCH as BATCH_011
from .import_batch_012 import BATCH as BATCH_012
from .import_batch_013 import BATCH as BATCH_013
from .import_batch_014 import BATCH as BATCH_014
from .import_batch_015 import BATCH as BATCH_015
from .import_batch_016 import BATCH as BATCH_016
from .import_batch_017 import BATCH as BATCH_017
from .import_batch_018 import BATCH as BATCH_018
from .import_batch_019 import BATCH as BATCH_019
from .import_batch_020 import BATCH as BATCH_020
from .import_batch_021 import BATCH as BATCH_021
from .import_batch_022 import BATCH as BATCH_022
from .import_batch_023 import BATCH as BATCH_023
from .import_batch_024 import BATCH as BATCH_024
from .import_batch_025 import BATCH as BATCH_025
from .import_batch_026 import BATCH as BATCH_026
from .import_batch_027 import BATCH as BATCH_027
from .import_batch_028 import BATCH as BATCH_028
from .import_batch_029 import BATCH as BATCH_029
from .import_batch_030 import BATCH as BATCH_030
from .import_batch_031 import BATCH as BATCH_031
from .import_batch_032 import BATCH as BATCH_032
from .import_batch_033 import BATCH as BATCH_033
from .import_batch_034 import BATCH as BATCH_034
from .import_batch_035 import BATCH as BATCH_035
from .import_batch_036 import BATCH as BATCH_036
from .import_batch_037 import BATCH as BATCH_037
from .import_batch_038 import BATCH as BATCH_038
from .import_batch_039 import BATCH as BATCH_039
from .import_batch_040 import BATCH as BATCH_040
from .import_batch_041 import BATCH as BATCH_041
from .import_batch_042 import BATCH as BATCH_042
from .import_batch_043 import BATCH as BATCH_043
from .import_batch_044 import BATCH as BATCH_044
from .import_batch_045 import BATCH as BATCH_045
from .import_batch_046 import BATCH as BATCH_046
from .import_batch_047 import BATCH as BATCH_047
from .import_batch_048 import BATCH as BATCH_048
from .import_batch_049 import BATCH as BATCH_049
from .import_batch_050 import BATCH as BATCH_050
from .import_batch_051 import BATCH as BATCH_051
from .import_batch_052 import BATCH as BATCH_052
from .import_batch_053 import BATCH as BATCH_053
from .import_batch_054 import BATCH as BATCH_054
from .import_batch_055 import BATCH as BATCH_055
from .import_batch_055b import BATCH as BATCH_055B
from .import_batch_056 import BATCH as BATCH_056
from .import_batch_057 import BATCH as BATCH_057
from .import_batch_058 import BATCH as BATCH_058
from .import_batch_059 import BATCH as BATCH_059
from .import_batch_060 import BATCH as BATCH_060
from .import_batch_061 import BATCH as BATCH_061
from .import_batch_062 import BATCH as BATCH_062
from .import_batch_063 import BATCH as BATCH_063
from .import_batch_064 import BATCH as BATCH_064
from .import_batch_065 import BATCH as BATCH_065
from .import_batch_066 import BATCH as BATCH_066
from .import_batch_067 import BATCH as BATCH_067
from .import_batch_068 import BATCH as BATCH_068
from .import_batch_069 import BATCH as BATCH_069
from .import_batch_070 import BATCH as BATCH_070
from .import_batch_071 import BATCH as BATCH_071
from .import_batch_072 import BATCH as BATCH_072
from .import_batch_073 import BATCH as BATCH_073
from .import_batch_074 import BATCH as BATCH_074
from .import_batch_075 import BATCH as BATCH_075
from .import_batch_076 import BATCH as BATCH_076
from .import_batch_077 import BATCH as BATCH_077
from .import_batch_078 import BATCH as BATCH_078
from .import_batch_079 import BATCH as BATCH_079
from .import_batch_080 import BATCH as BATCH_080
from .import_batch_080b import BATCH as BATCH_080B
from .import_batch_081 import BATCH as BATCH_081
from .import_batch_081b import BATCH as BATCH_081B
from .import_batch_082 import BATCH as BATCH_082
from .import_batch_082b import BATCH as BATCH_082B
from .import_batch_083 import BATCH as BATCH_083
from .import_batch_084 import BATCH as BATCH_084
from .import_batch_084b import BATCH as BATCH_084B
from .import_batch_085 import BATCH as BATCH_085
from .import_batch_086 import BATCH as BATCH_086
from .import_batch_087 import BATCH as BATCH_087
from .import_batch_088 import BATCH as BATCH_088
from .import_batch_088b import BATCH as BATCH_088B
from .import_batch_089 import BATCH as BATCH_089
from .import_batch_089b import BATCH as BATCH_089B
from .import_batch_089c import BATCH as BATCH_089C
from .import_batch_090 import BATCH as BATCH_090
from .import_batch_090b import BATCH as BATCH_090B
from .import_batch_090c import BATCH as BATCH_090C
from .import_batch_091 import BATCH as BATCH_091
from .import_batch_091b import BATCH as BATCH_091B
from .import_batch_091c import BATCH as BATCH_091C
from .import_batch_092 import BATCH as BATCH_092
from .import_batch_092b import BATCH as BATCH_092B
from .import_batch_093 import BATCH as BATCH_093
from .import_batch_093b import BATCH as BATCH_093B
from .import_batch_094 import BATCH as BATCH_094
from .import_batch_094b import BATCH as BATCH_094B
from .import_batch_095 import BATCH as BATCH_095
from .import_batch_095b import BATCH as BATCH_095B
from .import_batch_096 import BATCH as BATCH_096
from .import_batch_096b import BATCH as BATCH_096B
from .import_batch_097 import BATCH as BATCH_097
from .import_batch_097b import BATCH as BATCH_097B
from .import_batch_098 import BATCH as BATCH_098
from .import_batch_098b import BATCH as BATCH_098B
from .import_batch_099 import BATCH as BATCH_099
from .import_batch_099b import BATCH as BATCH_099B
from .import_batch_100 import BATCH as BATCH_100
from .import_batch_100b import BATCH as BATCH_100B
from .import_batch_100c import BATCH as BATCH_100C
from .import_batch_101 import BATCH as BATCH_101
from .import_batch_101b import BATCH as BATCH_101B
from .import_batch_101c import BATCH as BATCH_101C
from .import_batch_102 import BATCH as BATCH_102
from .import_batch_102b import BATCH as BATCH_102B
from .import_batch_102c import BATCH as BATCH_102C
from .import_batch_103 import BATCH as BATCH_103
from .import_batch_103b import BATCH as BATCH_103B
from .import_batch_103c import BATCH as BATCH_103C
from .import_batch_103d import BATCH as BATCH_103D
from .import_batch_104 import BATCH as BATCH_104
from .import_batch_104b import BATCH as BATCH_104B
from .import_batch_104c import BATCH as BATCH_104C
from .import_batch_104d import BATCH as BATCH_104D
from .import_batch_105 import BATCH as BATCH_105
from .import_batch_105b import BATCH as BATCH_105B
from .import_batch_105c import BATCH as BATCH_105C
from .import_batch_105d import BATCH as BATCH_105D
from .import_batch_106 import BATCH as BATCH_106
from .import_batch_106b import BATCH as BATCH_106B
from .import_batch_106c import BATCH as BATCH_106C
from .import_batch_106d import BATCH as BATCH_106D
from .import_batch_107 import BATCH as BATCH_107
from .import_batch_107b import BATCH as BATCH_107B
from .import_batch_107c import BATCH as BATCH_107C
from .import_batch_107d import BATCH as BATCH_107D
from .import_batch_108 import BATCH as BATCH_108
from .import_batch_108b import BATCH as BATCH_108B
from .import_batch_108c import BATCH as BATCH_108C
from .import_batch_108d import BATCH as BATCH_108D
from .import_batch_108e import BATCH as BATCH_108E
from .import_batch_109 import BATCH as BATCH_109
from .import_batch_109b import BATCH as BATCH_109B
from .import_batch_109c import BATCH as BATCH_109C
from .import_batch_109d import BATCH as BATCH_109D
from .import_batch_110 import BATCH as BATCH_110
from .import_batch_110b import BATCH as BATCH_110B
from .import_batch_110c import BATCH as BATCH_110C
from .import_batch_110d import BATCH as BATCH_110D
from .import_batch_111 import BATCH as BATCH_111
from .import_batch_111b import BATCH as BATCH_111B
from .import_batch_111c import BATCH as BATCH_111C
from .import_batch_111d import BATCH as BATCH_111D
from .import_batch_112 import BATCH as BATCH_112
from .import_batch_112b import BATCH as BATCH_112B
from .import_batch_112c import BATCH as BATCH_112C
from .import_batch_112d import BATCH as BATCH_112D
from .import_batch_113 import BATCH as BATCH_113
from .import_batch_113b import BATCH as BATCH_113B
from .import_batch_113c import BATCH as BATCH_113C
from .import_batch_113d import BATCH as BATCH_113D
from .import_batch_114 import BATCH as BATCH_114
from .import_batch_114b import BATCH as BATCH_114B
from .import_batch_114c import BATCH as BATCH_114C
from .import_batch_114d import BATCH as BATCH_114D
from .import_batch_115 import BATCH as BATCH_115
from .import_batch_115b import BATCH as BATCH_115B
from .import_batch_115c import BATCH as BATCH_115C
from .import_batch_115d import BATCH as BATCH_115D
from .import_batch_116 import BATCH as BATCH_116
from .import_batch_116b import BATCH as BATCH_116B
from .import_batch_116c import BATCH as BATCH_116C
from .import_batch_116d import BATCH as BATCH_116D
from .import_batch_117 import BATCH as BATCH_117
from .import_batch_117b import BATCH as BATCH_117B
from .import_batch_117c import BATCH as BATCH_117C
from .import_batch_117d import BATCH as BATCH_117D
from .import_batch_118 import BATCH as BATCH_118
from .import_batch_118b import BATCH as BATCH_118B
from .import_batch_118c import BATCH as BATCH_118C
from .import_batch_118d import BATCH as BATCH_118D
from .import_batch_119 import BATCH as BATCH_119
from .import_batch_119b import BATCH as BATCH_119B
from .import_batch_119c import BATCH as BATCH_119C
from .import_batch_119d import BATCH as BATCH_119D
from .import_batch_120 import BATCH as BATCH_120
from .import_batch_120b import BATCH as BATCH_120B
from .import_batch_120c import BATCH as BATCH_120C
from .import_batch_120d import BATCH as BATCH_120D
from .import_batch_121 import BATCH as BATCH_121
from .import_batch_121b import BATCH as BATCH_121B
from .import_batch_121c import BATCH as BATCH_121C
from .import_batch_121d import BATCH as BATCH_121D
from .import_batch_122 import BATCH as BATCH_122
from .import_batch_122b import BATCH as BATCH_122B
from .import_batch_122c import BATCH as BATCH_122C
from .import_batch_122d import BATCH as BATCH_122D
from .import_batch_123 import BATCH as BATCH_123
from .import_batch_123b import BATCH as BATCH_123B
from .import_batch_123c import BATCH as BATCH_123C
from .import_batch_124 import BATCH as BATCH_124
from .import_batch_124b import BATCH as BATCH_124B
from .import_batch_124c import BATCH as BATCH_124C
from .import_batch_124d import BATCH as BATCH_124D
from .import_batch_125 import BATCH as BATCH_125
from .import_batch_125b import BATCH as BATCH_125B
from .import_batch_125c import BATCH as BATCH_125C
from .import_batch_125d import BATCH as BATCH_125D
from .import_batch_126 import BATCH as BATCH_126
from .import_batch_126b import BATCH as BATCH_126B
from .import_batch_126c import BATCH as BATCH_126C
from .import_batch_126d import BATCH as BATCH_126D
from .import_batch_127 import BATCH as BATCH_127
from .import_batch_127b import BATCH as BATCH_127B
from .import_batch_127c import BATCH as BATCH_127C
from .import_batch_128 import BATCH as BATCH_128
from .import_batch_128b import BATCH as BATCH_128B
from .import_batch_129 import BATCH as BATCH_129
from .import_batch_129b import BATCH as BATCH_129B
from .import_batch_130 import BATCH as BATCH_130
from .import_batch_130b import BATCH as BATCH_130B
from .import_batch_131 import BATCH as BATCH_131
from .import_batch_131b import BATCH as BATCH_131B
from .import_batch_132 import BATCH as BATCH_132
from .import_batch_132b import BATCH as BATCH_132B
from .import_batch_133 import BATCH as BATCH_133
from .import_batch_134 import BATCH as BATCH_134
from .import_batch_134b import BATCH as BATCH_134B
from .import_batch_135 import BATCH as BATCH_135
from .import_batch_135b import BATCH as BATCH_135B
from .import_batch_136 import BATCH as BATCH_136
from .import_batch_137 import BATCH as BATCH_137
from .import_batch_138 import BATCH as BATCH_138
from .import_batch_139 import BATCH as BATCH_139
from .import_batch_140 import BATCH as BATCH_140
from .import_batch_141 import BATCH as BATCH_141
from .import_batch_142 import BATCH as BATCH_142
from .import_batch_143 import BATCH as BATCH_143
from .import_batch_144 import BATCH as BATCH_144
from .import_batch_145 import BATCH as BATCH_145
from .import_batch_146 import BATCH as BATCH_146
from .import_batch_147 import BATCH as BATCH_147
from .import_batch_148 import BATCH as BATCH_148
from .import_batch_149 import BATCH as BATCH_149
from .import_batch_150 import BATCH as BATCH_150
from .import_batch_151 import BATCH as BATCH_151
from .import_batch_152 import BATCH as BATCH_152
from .import_batch_153 import BATCH as BATCH_153
from .import_batch_154 import BATCH as BATCH_154
from .import_batch_155 import BATCH as BATCH_155
from .import_batch_156 import BATCH as BATCH_156
from .import_batch_157 import BATCH as BATCH_157
from .import_batch_158 import BATCH as BATCH_158
from .import_batch_159 import BATCH as BATCH_159
from .import_batch_160 import BATCH as BATCH_160
from .import_batch_161 import BATCH as BATCH_161
from .import_batch_162 import BATCH as BATCH_162
from .import_batch_163 import BATCH as BATCH_163
from .import_batch_164 import BATCH as BATCH_164
from .import_batch_165 import BATCH as BATCH_165
from .import_batch_166 import BATCH as BATCH_166
from .import_batch_167 import BATCH as BATCH_167
from .import_batch_168 import BATCH as BATCH_168
from .import_batch_169 import BATCH as BATCH_169
from .import_batch_170 import BATCH as BATCH_170
from .import_batch_171 import BATCH as BATCH_171
from .import_batch_172 import BATCH as BATCH_172
from .import_batch_173 import BATCH as BATCH_173
from .import_batch_174 import BATCH as BATCH_174
from .import_batch_175 import BATCH as BATCH_175
from .import_batch_176 import BATCH as BATCH_176
from .import_batch_177 import BATCH as BATCH_177
from .import_batch_178 import BATCH as BATCH_178
from .import_batch_179 import BATCH as BATCH_179
from .import_batch_180 import BATCH as BATCH_180
from .import_batch_181 import BATCH as BATCH_181
from .import_batch_182 import BATCH as BATCH_182
from .import_batch_183 import BATCH as BATCH_183
from .import_batch_184 import BATCH as BATCH_184
from .import_batch_185 import BATCH as BATCH_185
from .import_batch_186 import BATCH as BATCH_186
from .import_batch_187a import BATCH as BATCH_187A
from .import_batch_187b import BATCH as BATCH_187B
from .import_batch_187c import BATCH as BATCH_187C
from .import_batch_187d import BATCH as BATCH_187D
from .import_batch_188a import BATCH as BATCH_188A
from .import_batch_188b import BATCH as BATCH_188B
from .import_batch_188c import BATCH as BATCH_188C
from .import_batch_188d import BATCH as BATCH_188D
from .import_batch_189a import BATCH as BATCH_189A
from .import_batch_189b import BATCH as BATCH_189B
from .import_batch_189c import BATCH as BATCH_189C
from .import_batch_189d import BATCH as BATCH_189D
from .import_batch_190a import BATCH as BATCH_190A
from .import_batch_190b import BATCH as BATCH_190B
from .import_batch_190c import BATCH as BATCH_190C
from .import_batch_190d import BATCH as BATCH_190D
from .import_batch_191a import BATCH as BATCH_191A
from .import_batch_191b import BATCH as BATCH_191B
from .import_batch_192a import BATCH as BATCH_192A
from .import_batch_192b import BATCH as BATCH_192B
from .import_batch_192c import BATCH as BATCH_192C
from .import_batch_192d import BATCH as BATCH_192D
from .import_batch_193a import BATCH as BATCH_193A
from .import_batch_193b import BATCH as BATCH_193B
from .import_batch_193c import BATCH as BATCH_193C
from .import_batch_193d import BATCH as BATCH_193D
from .import_batch_194a import BATCH as BATCH_194A
from .import_batch_194b import BATCH as BATCH_194B
from .import_batch_194c import BATCH as BATCH_194C
from .import_batch_194d import BATCH as BATCH_194D
from .import_batch_195a import BATCH as BATCH_195A
from .import_batch_195b import BATCH as BATCH_195B
from .import_batch_195c import BATCH as BATCH_195C
from .import_batch_195d import BATCH as BATCH_195D
from .import_batch_196a import BATCH as BATCH_196A
from .import_batch_196b import BATCH as BATCH_196B
from .import_batch_196c import BATCH as BATCH_196C
from .import_batch_196d import BATCH as BATCH_196D
from .import_batch_197a import BATCH as BATCH_197A
from .import_batch_197b import BATCH as BATCH_197B
from .import_batch_197c import BATCH as BATCH_197C
from .import_batch_197d import BATCH as BATCH_197D
from .import_batch_198a import BATCH as BATCH_198A
from .import_batch_198b import BATCH as BATCH_198B
from .import_batch_198c import BATCH as BATCH_198C
from .import_batch_198d import BATCH as BATCH_198D
from .import_batch_198e import BATCH as BATCH_198E
from .import_batch_199a import BATCH as BATCH_199A
from .import_batch_199b import BATCH as BATCH_199B
from .import_batch_199c import BATCH as BATCH_199C
from .import_batch_199d import BATCH as BATCH_199D
from .import_batch_199e import BATCH as BATCH_199E
from .import_batch_200a import BATCH as BATCH_200A
from .import_batch_200b import BATCH as BATCH_200B
from .import_batch_200c import BATCH as BATCH_200C
from .import_batch_200d import BATCH as BATCH_200D
from .import_batch_200e import BATCH as BATCH_200E
from .import_batch_201a import BATCH as BATCH_201A
from .import_batch_201b import BATCH as BATCH_201B
from .import_batch_201c import BATCH as BATCH_201C
from .import_batch_201d import BATCH as BATCH_201D
from .import_batch_201e import BATCH as BATCH_201E
from .import_batch_202a import BATCH as BATCH_202A
from .import_batch_202b import BATCH as BATCH_202B
from .import_batch_202c import BATCH as BATCH_202C
from .import_batch_202d import BATCH as BATCH_202D
from .import_batch_202e import BATCH as BATCH_202E
from .import_batch_203a import BATCH as BATCH_203A
from .import_batch_203b import BATCH as BATCH_203B
from .import_batch_203c import BATCH as BATCH_203C
from .import_batch_203d import BATCH as BATCH_203D
from .import_batch_203e import BATCH as BATCH_203E
from .import_batch_204a import BATCH as BATCH_204A
from .import_batch_204b import BATCH as BATCH_204B
from .import_batch_204c import BATCH as BATCH_204C
from .import_batch_204d import BATCH as BATCH_204D
from .import_batch_205a import BATCH as BATCH_205A
from .import_batch_205b import BATCH as BATCH_205B
from .import_batch_205c import BATCH as BATCH_205C
from .import_batch_205d import BATCH as BATCH_205D
from .import_batch_206a import BATCH as BATCH_206A
from .import_batch_206b import BATCH as BATCH_206B
from .import_batch_206c import BATCH as BATCH_206C
from .import_batch_206d import BATCH as BATCH_206D
from .import_batch_207a import BATCH as BATCH_207A
from .import_batch_207b import BATCH as BATCH_207B
from .import_batch_207c import BATCH as BATCH_207C
from .import_batch_207d import BATCH as BATCH_207D
from .import_batch_207e import BATCH as BATCH_207E
from .import_batch_208a import BATCH as BATCH_208A
from .import_batch_208b import BATCH as BATCH_208B
from .import_batch_208c import BATCH as BATCH_208C
from .import_batch_208d import BATCH as BATCH_208D
from .import_batch_209a import BATCH as BATCH_209A
from .import_batch_209b import BATCH as BATCH_209B
from .import_batch_209c import BATCH as BATCH_209C
from .import_batch_209d import BATCH as BATCH_209D
from .import_batch_210a import BATCH as BATCH_210A
from .import_batch_210b import BATCH as BATCH_210B
from .import_batch_210c import BATCH as BATCH_210C
from .import_batch_210d import BATCH as BATCH_210D
from .import_batch_211a import BATCH as BATCH_211A
from .import_batch_211b import BATCH as BATCH_211B
from .import_batch_211c import BATCH as BATCH_211C
from .import_batch_211d import BATCH as BATCH_211D
from .import_batch_212a import BATCH as BATCH_212A
from .import_batch_212b import BATCH as BATCH_212B
from .import_batch_212c import BATCH as BATCH_212C
from .import_batch_212d import BATCH as BATCH_212D
from .import_batch_213a import BATCH as BATCH_213A
from .import_batch_213b import BATCH as BATCH_213B
from .import_batch_213c import BATCH as BATCH_213C
from .import_batch_213d import BATCH as BATCH_213D
from .import_batch_214a import BATCH as BATCH_214A
from .import_batch_214b import BATCH as BATCH_214B
from .import_batch_214c import BATCH as BATCH_214C
from .import_batch_214d import BATCH as BATCH_214D
from .import_batch_215a import BATCH as BATCH_215A
from .import_batch_215b import BATCH as BATCH_215B
from .import_batch_215c import BATCH as BATCH_215C
from .import_batch_215d import BATCH as BATCH_215D
from .import_batch_216a import BATCH as BATCH_216A
from .import_batch_216b import BATCH as BATCH_216B
from .import_batch_216c import BATCH as BATCH_216C
from .import_batch_216d import BATCH as BATCH_216D
from .import_batch_217a import BATCH as BATCH_217A
from .import_batch_217b import BATCH as BATCH_217B
from .import_batch_217c import BATCH as BATCH_217C
from .import_batch_217d import BATCH as BATCH_217D
from .import_batch_218a import BATCH as BATCH_218A
from .import_batch_218b import BATCH as BATCH_218B
from .import_batch_218c import BATCH as BATCH_218C
from .import_batch_218d import BATCH as BATCH_218D
from .import_batch_219a import BATCH as BATCH_219A
from .import_batch_219b import BATCH as BATCH_219B
from .import_batch_219c import BATCH as BATCH_219C
from .import_batch_219d import BATCH as BATCH_219D
from .import_batch_220a import BATCH as BATCH_220A
from .import_batch_220b import BATCH as BATCH_220B
from .import_batch_220c import BATCH as BATCH_220C
from .import_batch_220d import BATCH as BATCH_220D
from .import_batch_221a import BATCH as BATCH_221A
from .import_batch_221b import BATCH as BATCH_221B
from .import_batch_221c import BATCH as BATCH_221C
from .import_batch_221d import BATCH as BATCH_221D
from .import_batch_222a import BATCH as BATCH_222A
from .import_batch_222b import BATCH as BATCH_222B
from .import_batch_222c import BATCH as BATCH_222C
from .import_batch_222d import BATCH as BATCH_222D
from .import_batch_223a import BATCH as BATCH_223A
from .import_batch_223b import BATCH as BATCH_223B
from .import_batch_223c import BATCH as BATCH_223C
from .import_batch_223d import BATCH as BATCH_223D
from .import_batch_224a import BATCH as BATCH_224A
from .import_batch_224b import BATCH as BATCH_224B
from .import_batch_224c import BATCH as BATCH_224C
from .import_batch_224d import BATCH as BATCH_224D
from .import_batch_225a import BATCH as BATCH_225A
from .import_batch_225b import BATCH as BATCH_225B
from .import_batch_225c import BATCH as BATCH_225C
from .import_batch_225d import BATCH as BATCH_225D
from .import_batch_226a import BATCH as BATCH_226A
from .import_batch_226b import BATCH as BATCH_226B
from .import_batch_226c import BATCH as BATCH_226C
from .import_batch_226d import BATCH as BATCH_226D
from .import_batch_227a import BATCH as BATCH_227A
from .import_batch_227b import BATCH as BATCH_227B
from .import_batch_227c import BATCH as BATCH_227C
from .import_batch_227d import BATCH as BATCH_227D
from .import_batch_228a import BATCH as BATCH_228A
from .import_batch_228b import BATCH as BATCH_228B
from .import_batch_228c import BATCH as BATCH_228C
from .import_batch_228d import BATCH as BATCH_228D
from .import_batch_229a import BATCH as BATCH_229A
from .import_batch_229b import BATCH as BATCH_229B
from .import_batch_229c import BATCH as BATCH_229C
from .import_batch_229d import BATCH as BATCH_229D
from .import_batch_230a import BATCH as BATCH_230A
from .import_batch_230b import BATCH as BATCH_230B
from .import_batch_230c import BATCH as BATCH_230C
from .import_batch_230d import BATCH as BATCH_230D
from .import_batch_231a import BATCH as BATCH_231A
from .import_batch_231b import BATCH as BATCH_231B
from .import_batch_231c import BATCH as BATCH_231C
from .import_batch_231d import BATCH as BATCH_231D
from .import_batch_232a import BATCH as BATCH_232A
from .import_batch_232b import BATCH as BATCH_232B
from .import_batch_232c import BATCH as BATCH_232C
from .import_batch_232d import BATCH as BATCH_232D
from .import_batch_233a import BATCH as BATCH_233A
from .import_batch_233b import BATCH as BATCH_233B
from .import_batch_233c import BATCH as BATCH_233C
from .import_batch_233d import BATCH as BATCH_233D
from .import_batch_234a import BATCH as BATCH_234A
from .catalog_evidence import judge_contract_hash
from .catalog_artifacts import write_json_atomic
from .schemas import ProblemDefinition, TestCase
from .starter_code import with_support_classes
from .validation import compare_result, run_source

ROOT = Path(__file__).resolve().parent.parent
VALIDATION_PROTOCOL_VERSION = 2
BATCH = {**BATCH_001, **BATCH_002, **BATCH_003, **BATCH_004, **BATCH_005, **BATCH_006, **BATCH_007, **BATCH_008, **BATCH_009, **BATCH_010, **BATCH_011, **BATCH_012, **BATCH_013, **BATCH_014, **BATCH_015, **BATCH_016, **BATCH_017, **BATCH_018, **BATCH_019, **BATCH_020, **BATCH_021, **BATCH_022, **BATCH_023, **BATCH_024, **BATCH_025, **BATCH_026, **BATCH_027, **BATCH_028, **BATCH_029, **BATCH_030, **BATCH_031, **BATCH_032, **BATCH_033, **BATCH_034, **BATCH_035, **BATCH_036}


BATCH.update(BATCH_037)
BATCH.update(BATCH_038)
BATCH.update(BATCH_039)
BATCH.update(BATCH_040)
BATCH.update(BATCH_041)
BATCH.update(BATCH_042)
BATCH.update(BATCH_043)
BATCH.update(BATCH_044)
BATCH.update(BATCH_045)
BATCH.update(BATCH_046)
BATCH.update(BATCH_047)
BATCH.update(BATCH_048)
BATCH.update(BATCH_049)
BATCH.update(BATCH_050)
BATCH.update(BATCH_051)
BATCH.update(BATCH_052)
BATCH.update(BATCH_053)
BATCH.update(BATCH_054)
BATCH.update(BATCH_055)
BATCH.update(BATCH_055B)
BATCH.update(BATCH_056)
BATCH.update(BATCH_057)
BATCH.update(BATCH_058)
BATCH.update(BATCH_059)
BATCH.update(BATCH_060)
BATCH.update(BATCH_061)
BATCH.update(BATCH_062)
BATCH.update(BATCH_063)
BATCH.update(BATCH_064)
BATCH.update(BATCH_065)
BATCH.update(BATCH_066)
BATCH.update(BATCH_067)
BATCH.update(BATCH_068)
BATCH.update(BATCH_069)
BATCH.update(BATCH_070)
BATCH.update(BATCH_071)
BATCH.update(BATCH_072)
BATCH.update(BATCH_073)
BATCH.update(BATCH_074)
BATCH.update(BATCH_075)
BATCH.update(BATCH_076)
BATCH.update(BATCH_077)
BATCH.update(BATCH_078)
BATCH.update(BATCH_079)
BATCH.update(BATCH_080)
BATCH.update(BATCH_080B)
BATCH.update(BATCH_081)
BATCH.update(BATCH_081B)
BATCH.update(BATCH_082)
BATCH.update(BATCH_082B)
BATCH.update(BATCH_083)
BATCH.update(BATCH_084)
BATCH.update(BATCH_084B)
BATCH.update(BATCH_085)
BATCH.update(BATCH_086)
BATCH.update(BATCH_087)
BATCH.update(BATCH_088)
BATCH.update(BATCH_088B)
BATCH.update(BATCH_089)
BATCH.update(BATCH_089B)
BATCH.update(BATCH_089C)
BATCH.update(BATCH_090)
BATCH.update(BATCH_090B)
BATCH.update(BATCH_090C)
BATCH.update(BATCH_091)
BATCH.update(BATCH_091B)
BATCH.update(BATCH_091C)
BATCH.update(BATCH_092)
BATCH.update(BATCH_092B)
BATCH.update(BATCH_093)
BATCH.update(BATCH_093B)
BATCH.update(BATCH_094)
BATCH.update(BATCH_094B)
BATCH.update(BATCH_095)
BATCH.update(BATCH_095B)
BATCH.update(BATCH_096)
BATCH.update(BATCH_096B)
BATCH.update(BATCH_097)
BATCH.update(BATCH_097B)
BATCH.update(BATCH_098)
BATCH.update(BATCH_098B)
BATCH.update(BATCH_099)
BATCH.update(BATCH_099B)
BATCH.update(BATCH_100)
BATCH.update(BATCH_100B)
BATCH.update(BATCH_100C)
BATCH.update(BATCH_101)
BATCH.update(BATCH_101B)
BATCH.update(BATCH_101C)
BATCH.update(BATCH_102)
BATCH.update(BATCH_102B)
BATCH.update(BATCH_102C)
BATCH.update(BATCH_103)
BATCH.update(BATCH_103B)
BATCH.update(BATCH_103C)
BATCH.update(BATCH_103D)
BATCH.update(BATCH_104)
BATCH.update(BATCH_104B)
BATCH.update(BATCH_104C)
BATCH.update(BATCH_104D)
BATCH.update(BATCH_105)
BATCH.update(BATCH_105B)
BATCH.update(BATCH_105C)
BATCH.update(BATCH_105D)
BATCH.update(BATCH_106)
BATCH.update(BATCH_106B)
BATCH.update(BATCH_106C)
BATCH.update(BATCH_106D)
BATCH.update(BATCH_107)
BATCH.update(BATCH_107B)
BATCH.update(BATCH_107C)
BATCH.update(BATCH_107D)
BATCH.update(BATCH_108)
BATCH.update(BATCH_108B)
BATCH.update(BATCH_108C)
BATCH.update(BATCH_108D)
BATCH.update(BATCH_108E)
BATCH.update(BATCH_109)
BATCH.update(BATCH_109B)
BATCH.update(BATCH_109C)
BATCH.update(BATCH_109D)
BATCH.update(BATCH_110)
BATCH.update(BATCH_110B)
BATCH.update(BATCH_110C)
BATCH.update(BATCH_110D)
BATCH.update(BATCH_111)
BATCH.update(BATCH_111B)
BATCH.update(BATCH_111C)
BATCH.update(BATCH_111D)
BATCH.update(BATCH_112)
BATCH.update(BATCH_112B)
BATCH.update(BATCH_112C)
BATCH.update(BATCH_112D)
BATCH.update(BATCH_113)
BATCH.update(BATCH_113B)
BATCH.update(BATCH_113C)
BATCH.update(BATCH_113D)
BATCH.update(BATCH_114)
BATCH.update(BATCH_114B)
BATCH.update(BATCH_114C)
BATCH.update(BATCH_114D)
BATCH.update(BATCH_115)
BATCH.update(BATCH_115B)
BATCH.update(BATCH_115C)
BATCH.update(BATCH_115D)
BATCH.update(BATCH_116)
BATCH.update(BATCH_116B)
BATCH.update(BATCH_116C)
BATCH.update(BATCH_116D)
BATCH.update(BATCH_117)
BATCH.update(BATCH_117B)
BATCH.update(BATCH_117C)
BATCH.update(BATCH_117D)
BATCH.update(BATCH_118)
BATCH.update(BATCH_118B)
BATCH.update(BATCH_118C)
BATCH.update(BATCH_118D)
BATCH.update(BATCH_119)
BATCH.update(BATCH_119B)
BATCH.update(BATCH_119C)
BATCH.update(BATCH_119D)
BATCH.update(BATCH_120)
BATCH.update(BATCH_120B)
BATCH.update(BATCH_120C)
BATCH.update(BATCH_120D)
BATCH.update(BATCH_121)
BATCH.update(BATCH_121B)
BATCH.update(BATCH_121C)
BATCH.update(BATCH_121D)
BATCH.update(BATCH_122)
BATCH.update(BATCH_122B)
BATCH.update(BATCH_122C)
BATCH.update(BATCH_122D)
BATCH.update(BATCH_123)
BATCH.update(BATCH_123B)
BATCH.update(BATCH_123C)
BATCH.update(BATCH_124)
BATCH.update(BATCH_124B)
BATCH.update(BATCH_124C)
BATCH.update(BATCH_124D)
BATCH.update(BATCH_125)
BATCH.update(BATCH_125B)
BATCH.update(BATCH_125C)
BATCH.update(BATCH_125D)
BATCH.update(BATCH_126)
BATCH.update(BATCH_126B)
BATCH.update(BATCH_126C)
BATCH.update(BATCH_126D)
BATCH.update(BATCH_127)
BATCH.update(BATCH_127B)
BATCH.update(BATCH_127C)
BATCH.update(BATCH_128)
BATCH.update(BATCH_128B)
BATCH.update(BATCH_129)
BATCH.update(BATCH_129B)
BATCH.update(BATCH_130)
BATCH.update(BATCH_130B)
BATCH.update(BATCH_131)
BATCH.update(BATCH_131B)
BATCH.update(BATCH_132)
BATCH.update(BATCH_132B)
BATCH.update(BATCH_133)
BATCH.update(BATCH_134)
BATCH.update(BATCH_134B)
BATCH.update(BATCH_135)
BATCH.update(BATCH_135B)
BATCH.update(BATCH_136)
BATCH.update(BATCH_137)
BATCH.update(BATCH_138)
BATCH.update(BATCH_139)
BATCH.update(BATCH_140)
BATCH.update(BATCH_141)
BATCH.update(BATCH_142)
BATCH.update(BATCH_143)
BATCH.update(BATCH_144)
BATCH.update(BATCH_145)
BATCH.update(BATCH_146)
BATCH.update(BATCH_147)
BATCH.update(BATCH_148)
BATCH.update(BATCH_149)
BATCH.update(BATCH_150)
BATCH.update(BATCH_151)
BATCH.update(BATCH_152)
BATCH.update(BATCH_153)
BATCH.update(BATCH_154)
BATCH.update(BATCH_155)
BATCH.update(BATCH_156)
BATCH.update(BATCH_157)
BATCH.update(BATCH_158)
BATCH.update(BATCH_159)
BATCH.update(BATCH_160)
BATCH.update(BATCH_161)
BATCH.update(BATCH_162)
BATCH.update(BATCH_163)
BATCH.update(BATCH_164)
BATCH.update(BATCH_165)
BATCH.update(BATCH_166)
BATCH.update(BATCH_167)
BATCH.update(BATCH_168)
BATCH.update(BATCH_169)
BATCH.update(BATCH_170)
BATCH.update(BATCH_171)
BATCH.update(BATCH_172)
BATCH.update(BATCH_173)
BATCH.update(BATCH_174)
BATCH.update(BATCH_175)
BATCH.update(BATCH_176)
BATCH.update(BATCH_177)
BATCH.update(BATCH_178)
BATCH.update(BATCH_179)
BATCH.update(BATCH_180)
BATCH.update(BATCH_181)
BATCH.update(BATCH_182)
BATCH.update(BATCH_183)
BATCH.update(BATCH_184)
BATCH.update(BATCH_185)
BATCH.update(BATCH_186)
BATCH.update(BATCH_187A)
BATCH.update(BATCH_187B)
BATCH.update(BATCH_187C)
BATCH.update(BATCH_187D)
BATCH.update(BATCH_188A)
BATCH.update(BATCH_188B)
BATCH.update(BATCH_188C)
BATCH.update(BATCH_188D)
BATCH.update(BATCH_189A)
BATCH.update(BATCH_189B)
BATCH.update(BATCH_189C)
BATCH.update(BATCH_189D)
BATCH.update(BATCH_190A)
BATCH.update(BATCH_190B)
BATCH.update(BATCH_190C)
BATCH.update(BATCH_190D)
BATCH.update(BATCH_191A)
BATCH.update(BATCH_191B)
BATCH.update(BATCH_192A)
BATCH.update(BATCH_192B)
BATCH.update(BATCH_192C)
BATCH.update(BATCH_192D)
BATCH.update(BATCH_193A)
BATCH.update(BATCH_193B)
BATCH.update(BATCH_193C)
BATCH.update(BATCH_193D)
BATCH.update(BATCH_194A)
BATCH.update(BATCH_194B)
BATCH.update(BATCH_194C)
BATCH.update(BATCH_194D)
BATCH.update(BATCH_195A)
BATCH.update(BATCH_195B)
BATCH.update(BATCH_195C)
BATCH.update(BATCH_195D)
BATCH.update(BATCH_196A)
BATCH.update(BATCH_196B)
BATCH.update(BATCH_196C)
BATCH.update(BATCH_196D)
BATCH.update(BATCH_197A)
BATCH.update(BATCH_197B)
BATCH.update(BATCH_197C)
BATCH.update(BATCH_197D)
BATCH.update(BATCH_198A)
BATCH.update(BATCH_198B)
BATCH.update(BATCH_198C)
BATCH.update(BATCH_198D)
BATCH.update(BATCH_198E)
BATCH.update(BATCH_199A)
BATCH.update(BATCH_199B)
BATCH.update(BATCH_199C)
BATCH.update(BATCH_199D)
BATCH.update(BATCH_199E)
BATCH.update(BATCH_200A)
BATCH.update(BATCH_200B)
BATCH.update(BATCH_200C)
BATCH.update(BATCH_200D)
BATCH.update(BATCH_200E)
BATCH.update(BATCH_201A)
BATCH.update(BATCH_201B)
BATCH.update(BATCH_201C)
BATCH.update(BATCH_201D)
BATCH.update(BATCH_201E)
BATCH.update(BATCH_202A)
BATCH.update(BATCH_202B)
BATCH.update(BATCH_202C)
BATCH.update(BATCH_202D)
BATCH.update(BATCH_202E)
BATCH.update(BATCH_203A)
BATCH.update(BATCH_203B)
BATCH.update(BATCH_203C)
BATCH.update(BATCH_203D)
BATCH.update(BATCH_203E)
BATCH.update(BATCH_204A)
BATCH.update(BATCH_204B)
BATCH.update(BATCH_204C)
BATCH.update(BATCH_204D)
BATCH.update(BATCH_205A)
BATCH.update(BATCH_205B)
BATCH.update(BATCH_205C)
BATCH.update(BATCH_205D)
BATCH.update(BATCH_206A)
BATCH.update(BATCH_206B)
BATCH.update(BATCH_206C)
BATCH.update(BATCH_206D)
BATCH.update(BATCH_207A)
BATCH.update(BATCH_207B)
BATCH.update(BATCH_207C)
BATCH.update(BATCH_207D)
BATCH.update(BATCH_207E)
BATCH.update(BATCH_208A)
BATCH.update(BATCH_208B)
BATCH.update(BATCH_208C)
BATCH.update(BATCH_208D)
BATCH.update(BATCH_209A)
BATCH.update(BATCH_209B)
BATCH.update(BATCH_209C)
BATCH.update(BATCH_209D)
BATCH.update(BATCH_210A)
BATCH.update(BATCH_210B)
BATCH.update(BATCH_210C)
BATCH.update(BATCH_210D)
BATCH.update(BATCH_211A)
BATCH.update(BATCH_211B)
BATCH.update(BATCH_211C)
BATCH.update(BATCH_211D)
BATCH.update(BATCH_212A)
BATCH.update(BATCH_212B)
BATCH.update(BATCH_212C)
BATCH.update(BATCH_212D)
BATCH.update(BATCH_213A)
BATCH.update(BATCH_213B)
BATCH.update(BATCH_213C)
BATCH.update(BATCH_213D)
BATCH.update(BATCH_214A)
BATCH.update(BATCH_214B)
BATCH.update(BATCH_214C)
BATCH.update(BATCH_214D)
BATCH.update(BATCH_215A)
BATCH.update(BATCH_215B)
BATCH.update(BATCH_215C)
BATCH.update(BATCH_215D)
BATCH.update(BATCH_216A)
BATCH.update(BATCH_216B)
BATCH.update(BATCH_216C)
BATCH.update(BATCH_216D)
BATCH.update(BATCH_217A)
BATCH.update(BATCH_217B)
BATCH.update(BATCH_217C)
BATCH.update(BATCH_217D)
BATCH.update(BATCH_218A)
BATCH.update(BATCH_218B)
BATCH.update(BATCH_218C)
BATCH.update(BATCH_218D)
BATCH.update(BATCH_219A)
BATCH.update(BATCH_219B)
BATCH.update(BATCH_219C)
BATCH.update(BATCH_219D)
BATCH.update(BATCH_220A)
BATCH.update(BATCH_220B)
BATCH.update(BATCH_220C)
BATCH.update(BATCH_220D)
BATCH.update(BATCH_221A)
BATCH.update(BATCH_221B)
BATCH.update(BATCH_221C)
BATCH.update(BATCH_221D)
BATCH.update(BATCH_222A)
BATCH.update(BATCH_222B)
BATCH.update(BATCH_222C)
BATCH.update(BATCH_222D)
BATCH.update(BATCH_223A)
BATCH.update(BATCH_223B)
BATCH.update(BATCH_223C)
BATCH.update(BATCH_223D)
BATCH.update(BATCH_224A)
BATCH.update(BATCH_224B)
BATCH.update(BATCH_224C)
BATCH.update(BATCH_224D)
BATCH.update(BATCH_225A)
BATCH.update(BATCH_225B)
BATCH.update(BATCH_225C)
BATCH.update(BATCH_225D)
BATCH.update(BATCH_226A)
BATCH.update(BATCH_226B)
BATCH.update(BATCH_226C)
BATCH.update(BATCH_226D)
BATCH.update(BATCH_227A)
BATCH.update(BATCH_227B)
BATCH.update(BATCH_227C)
BATCH.update(BATCH_227D)
BATCH.update(BATCH_228A)
BATCH.update(BATCH_228B)
BATCH.update(BATCH_228C)
BATCH.update(BATCH_228D)
BATCH.update(BATCH_229A)
BATCH.update(BATCH_229B)
BATCH.update(BATCH_229C)
BATCH.update(BATCH_229D)
BATCH.update(BATCH_230A)
BATCH.update(BATCH_230B)
BATCH.update(BATCH_230C)
BATCH.update(BATCH_230D)
BATCH.update(BATCH_231A)
BATCH.update(BATCH_231B)
BATCH.update(BATCH_231C)
BATCH.update(BATCH_231D)
BATCH.update(BATCH_232A)
BATCH.update(BATCH_232B)
BATCH.update(BATCH_232C)
BATCH.update(BATCH_232D)
BATCH.update(BATCH_233A)
BATCH.update(BATCH_233B)
BATCH.update(BATCH_233C)
BATCH.update(BATCH_233D)
BATCH.update(BATCH_234A)


def digest(payload):
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def batch_implementation_hash(spec):
    """Hash the source that supplies this problem's oracle and generator."""
    return hashlib.sha256(Path(inspect.getsourcefile(spec["oracle"])).read_bytes()).hexdigest()


def validation_cache_key(spec, source_hash):
    """Stable evidence identity; bump the protocol only for semantic validator changes."""
    payload = {
        "protocol": VALIDATION_PROTOCOL_VERSION,
        "source_hash": source_hash,
        "batch_implementation_sha256": batch_implementation_hash(spec),
        "judge_contract_sha256": judge_contract_hash(),
    }
    return digest(payload)


def cached_validation_is_current(pid, spec, source_hash, record, root=ROOT):
    """Return true only for a complete, unchanged approved validation bundle."""
    if record.get("status") != "imported" or record.get("source_hash") != source_hash:
        return False
    try:
        report = json.loads((root / record["validation_report"]).read_text())
        candidate = json.loads((root / "catalog_import/candidates" / f"leetcode-{pid}.json").read_text())
        if not (report.get("valid") and report.get("problem_id") == f"leetcode-{pid}"
                and report.get("content_sha256") == digest(candidate)
                and report.get("source_hash") == source_hash
                and report.get("judge_contract_sha256") == judge_contract_hash()
                and report.get("batch_implementation_sha256") == batch_implementation_hash(spec)
                and report.get("reference_passed") == len(candidate["tests"])
                and report.get("visible_tests", 0) >= 2 and report.get("hidden_tests", 0) >= 12
                and report.get("oracle_inputs", 0) >= 500
                and len(report.get("wrong_solutions", [])) >= 2
                and all(w.get("failed_cases") for w in report["wrong_solutions"])):
            return False
        # Reports written before protocol v2 have equivalent evidence fields. They
        # remain reusable until their problem, source, oracle batch, or judge changes.
        return report.get("validation_cache_key") in {None, validation_cache_key(spec, source_hash)}
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError):
        return False


def workbook_sample(sample, parameters, result_mode="return", mutated_parameter=None):
    """Parse only JSON/Python literals in the workbook's input/output notation.

    Calls, attribute access, comprehensions, and arbitrary expressions are never
    evaluated. Unrecognized samples must be reviewed explicitly, not skipped.
    """
    if not sample:
        return None
    if not sample.startswith("Input ") or " → Output " not in sample:
        raise ValueError("Workbook sample needs manual parsing/reconciliation")
    arguments, output = sample[6:].split(" → Output ", 1)
    class JsonNames(ast.NodeTransformer):
        def visit_Name(self, node):
            if node.id in {"null", "true", "false"}:
                return ast.Constant({"null": None, "true": True, "false": False}[node.id])
            return node
    call = ast.parse(f"sample({arguments})", mode="eval").body
    if call.args:
        if call.keywords:
            raise ValueError("Mixed named/positional workbook inputs require review")
        args = [ast.literal_eval(JsonNames().visit(value)) for value in call.args]
    else:
        normalized = lambda name: name.replace("_", "").casefold()
        values = {normalized(k.arg): ast.literal_eval(JsonNames().visit(k.value)) for k in call.keywords if k.arg}
        if set(values) != {normalized(p["name"]) for p in parameters}:
            raise ValueError("Workbook parameter names do not match the reviewed signature")
        args = [values[normalized(p["name"])] for p in parameters]
    if len(args) != len(parameters):
        raise ValueError("Workbook argument count differs from the reviewed signature")
    value = output[:-1] if output.endswith(".") else output
    if result_mode == "returned_prefix":
        output_call = ast.parse(f"sample({value})", mode="eval").body
        if len(output_call.args) != 1 or len(output_call.keywords) != 1 or mutated_parameter is None:
            raise ValueError("Prefix sample requires one count and one updated list")
        count = ast.literal_eval(output_call.args[0])
        keyword = output_call.keywords[0]
        if keyword.arg != parameters[mutated_parameter]["name"] or not isinstance(keyword.value, ast.List):
            raise ValueError("Prefix sample must name the mutated list parameter")
        if type(count) is not int or not 0 <= count <= len(keyword.value.elts):
            raise ValueError("Invalid returned prefix length in workbook sample")
        values = []
        for index, element in enumerate(keyword.value.elts):
            if isinstance(element, ast.Name) and element.id == "_":
                if index < count:
                    raise ValueError("Unspecified values are only allowed after the checked prefix")
                values.append(None)
            else:
                values.append(ast.literal_eval(JsonNames().visit(element)))
        expected = {"return": count, "prefix": values[:count]}
    else:
        expected = ast.literal_eval(JsonNames().visit(ast.parse(value, mode="eval").body))
    return args, expected


def build(pid, spec, source):
    examples = spec["examples"]
    hidden = spec["boundaries"]
    comparator = spec.get("comparator", "exact")
    args_seen = {json.dumps(args, sort_keys=True) for args, _ in examples}
    hidden_keys = [json.dumps(args, sort_keys=True) for args in hidden]
    if len(hidden_keys) != len(set(hidden_keys)) or args_seen.intersection(hidden_keys):
        raise ValueError(f"{pid}: repeated test inputs")
    parameter_sources = spec.get("parameter_sources", {})
    parameters = [dict(name=n, annotation=a, adapter=d,
                       source_parameter=parameter_sources.get(index))
                  for index, (n, a, d) in enumerate(spec["params"])]
    mode = spec.get("result_mode", "return")
    sample_adapter = spec.get("sample_contract_adapter")
    if sample_adapter:
        if (set(sample_adapter) != {"source_sample", "arguments", "expected", "reason"}
                or sample_adapter["source_sample"] != source["sample"]
                or not isinstance(sample_adapter["reason"], str)
                or not sample_adapter["reason"].strip()):
            raise ValueError(f"{pid}: invalid or stale workbook sample contract adapter")
        sample = (sample_adapter["arguments"], sample_adapter["expected"])
    else:
        sample = workbook_sample(source["sample"], parameters, mode, spec.get("mutated_parameter"))
    correction = spec.get("sample_correction")
    if correction and sample is None:
        raise ValueError(f"{pid}: cannot correct a missing workbook sample")
    if sample is not None:
        args, expected = sample
        if correction:
            if (set(correction) != {"original_expected", "corrected_expected", "reason"}
                    or expected != correction["original_expected"]
                    or not isinstance(correction["reason"], str) or not correction["reason"].strip()
                    or compare_result(spec["oracle"](args), expected, comparator, mode)):
                raise ValueError(f"{pid}: invalid or stale workbook sample correction")
            expected = correction["corrected_expected"]
        if not compare_result(spec["oracle"](args), expected, comparator, mode):
            raise ValueError(f"{pid}: workbook sample conflicts with the independent oracle")
        if not any(example_args == args for example_args, _ in examples):
            raise ValueError(f"{pid}: the correct workbook sample must remain a visible example")
    test_inputs = [(a, True, explanation) for a, explanation in examples] + [(a, False, None) for a in hidden]
    tests = [dict(id=f"lc-{pid}-{i+1}", arguments=args, expected=spec["oracle"](args),
                  comparator=comparator, visible=visible, explanation=explanation)
             for i, (args, visible, explanation) in enumerate(test_inputs)]
    for i, (args, expected) in enumerate(spec.get("stress", [])):
        key = json.dumps(args, sort_keys=True)
        if key in args_seen or key in hidden_keys:
            raise ValueError(f"{pid}: stress input duplicates an example or hidden case")
        hidden_keys.append(key)
        tests.append(dict(id=f"lc-{pid}-stress-{i+1}", arguments=args, expected=expected,
                          comparator=comparator, visible=False))
    if spec.get("node_order"):
        for test in tests:
            test["expected_node_order"] = spec["node_order"](test["arguments"])
    rubric = {3: (1, 1, 1, 0, 0), 5: (2, 1, 1, 1, 0), 6: (2, 1, 1, 1, 1),
              7: (2, 2, 1, 1, 1), 8: (3, 2, 1, 1, 1)}[spec["difficulty"]]
    starter = f"def {spec['name']}({', '.join(n + ': ' + a for n, a, _ in spec['params'])}) -> {spec['returns']}:\n    # Write your solution here.\n    pass\n"
    statement = spec.get("statement", source["statement"])
    summary = statement.split(". ", 1)[0]
    payload = dict(id=f"leetcode-{pid}", version=spec.get("version", 1), status="approved", title=source["title"],
        summary=summary + ("." if not summary.endswith(".") else ""),
        statement=statement, constraints=spec["constraints"], topics=spec["topics"],
        prerequisites=spec.get("prerequisites", spec["topics"][:1] if spec["difficulty"] >= 8 else []),
        signature=dict(name=spec["name"], parameters=parameters, returns=spec["returns"], return_adapter=spec["adapter"],
                       node_policy=spec.get("node_policy", "values"), result_mode=mode,
                       mutated_parameter=spec.get("mutated_parameter"),
                       immutable_parameters=spec.get("immutable_parameters", [])),
        starter_code=with_support_classes(starter, [p["adapter"] for p in parameters] + [spec["adapter"]]),
        reference_solution=spec["reference"], brute_force_solution=None, known_wrong_solutions=spec["wrong"],
        target_time_complexity=spec["time"], target_space_complexity=spec["space"],
        estimated_minutes=20 if spec["difficulty"] <= 3 else 50 if spec["difficulty"] >= 8 else 35,
        rubric=dict(zip(("algorithmic_insight", "prerequisites", "implementation", "performance_pressure", "edge_cases"), rubric)),
        hints=spec["hints"], editorial=spec["editorial"], tests=tests)
    return ProblemDefinition.model_validate(payload)


def verify(problem, spec, source_hash):
    started = time.perf_counter()
    failures, rejected = [], []
    for case in problem.tests:
        ok, error = run_source(problem.reference_solution, problem, case)
        if not ok:
            failures.append({"phase": "deterministic", "case": case.id, "error": error})
    for index, wrong in enumerate(problem.known_wrong_solutions):
        evidence = []
        for case in problem.tests:
            ok, error = run_source(wrong, problem, case)
            # Require an algorithmic wrong answer, not syntax errors or an exception.
            if not ok and error is None:
                evidence.append(case.id)
        rejected.append({"reason": spec["wrong_reasons"][index], "failed_cases": evidence})
        if not evidence:
            failures.append({"phase": "known_wrong", "index": index})
    seed, checked = 4047 + int(problem.id.split("-")[-1]), 0
    rng = random.Random(seed)
    for i in range(500):
        args = spec["generator"](rng)
        case = TestCase(id=f"oracle-{i}", arguments=args, expected=spec["oracle"](args), comparator=spec.get("comparator", "exact"),
                        expected_node_order=spec["node_order"](args) if spec.get("node_order") else None)
        ok, error = run_source(problem.reference_solution, problem, case)
        if not ok:
            failures.append({"phase": "oracle", "case": i, "arguments": args, "error": error})
        checked += 1
    batch_path = Path(inspect.getsourcefile(spec["oracle"]))
    return {"valid": not failures, "problem_id": problem.id, "content_sha256": digest(problem.model_dump(mode="json")),
        "source_hash": source_hash, "visible_tests": sum(t.visible for t in problem.tests),
        "hidden_tests": sum(not t.visible for t in problem.tests),
        "reference_passed": len(problem.tests) - sum(f["phase"] == "deterministic" for f in failures),
        "wrong_solutions": rejected, "oracle_inputs": checked, "oracle_seed": seed,
        "oracle_implementation": f"code_practice/{batch_path.name}:{spec['oracle'].__name__}",
        "validator_implementation_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "batch_implementation_sha256": batch_implementation_hash(spec),
        "judge_contract_sha256": judge_contract_hash(),
        "validation_protocol_version": VALIDATION_PROTOCOL_VERSION,
        "validation_cache_key": validation_cache_key(spec, source_hash),
        "elapsed_seconds": round(time.perf_counter() - started, 3), "failures": failures}


def _review_child(pid, spec, source, source_hash, connection):
    try:
        problem = build(pid, spec, source)
        report = verify(problem, spec, source_hash)
        report["workbook_sample"] = "preserved and independently verified" if source["sample"] else "missing in workbook; reviewed examples authored"
        if spec.get("sample_contract_adapter"):
            report["workbook_sample"] = "source sample preserved through an explicit callable-context adapter"
            report["sample_contract_adapter"] = {
                **spec["sample_contract_adapter"],
                "source_reference": source["reference_url"],
            }
        if spec.get("sample_correction"):
            report["workbook_sample"] = "original input preserved; erroneous workbook output explicitly corrected"
            report["sample_correction"] = {**spec["sample_correction"], "original_sample": source["sample"],
                                           "source_reference": source["reference_url"]}
        connection.send((problem.model_dump(mode="json"), report))
    except Exception as error:
        connection.send((None, {"valid": False, "problem_id": f"leetcode-{pid}", "source_hash": source_hash,
                                "failures": [{"phase": "build", "error": f"{type(error).__name__}: {error}"}]}))
    finally:
        connection.close()


def review_isolated(pid, spec, source, source_hash, timeout_seconds=30):
    """One bounded child process per problem; a failure cannot poison the next."""
    context = multiprocessing.get_context("spawn")
    incoming, outgoing = context.Pipe(duplex=False)
    process = context.Process(target=_review_child, args=(pid, spec, source, source_hash, outgoing))
    try:
        process.start()
    except Exception as error:
        incoming.close()
        outgoing.close()
        return None, {
            "valid": False,
            "problem_id": f"leetcode-{pid}",
            "source_hash": source_hash,
            "failures": [{
                "phase": "isolated_validation_start",
                "error": f"{type(error).__name__}: {error}",
            }],
        }
    outgoing.close()
    try:
        if incoming.poll(timeout_seconds):
            try:
                return incoming.recv()
            except EOFError:
                message = "Validator exited before returning evidence"
        else:
            message = f"Validation exceeded {timeout_seconds} seconds"
        return None, {"valid": False, "problem_id": f"leetcode-{pid}", "source_hash": source_hash,
                      "failures": [{"phase": "isolated_validation", "error": message}]}
    finally:
        incoming.close()
        process.join(.2)
        if process.is_alive():
            process.terminate()
            process.join(2)
        if process.is_alive():
            process.kill()
            process.join(2)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ids", nargs="+", type=int)
    parser.add_argument("--timeout-seconds", type=float, default=30)
    parser.add_argument("--jobs", type=int, default=4, help="Concurrent isolated validators (1-4).")
    parser.add_argument("--force", action="store_true", help="Revalidate selected imports even when evidence is current.")
    args = parser.parse_args()
    if args.ids and any(pid not in BATCH for pid in args.ids):
        parser.error("Each requested ID must have a reviewed batch specification")
    if args.timeout_seconds <= 0:
        parser.error("Timeout must be positive")
    if not 1 <= args.jobs <= 4:
        parser.error("--jobs must be between 1 and 4")
    ledger_path = ROOT / "catalog_import/ledger.json"
    ledger = json.loads(ledger_path.read_text())
    sources = {s["source_id"]: s for line in (ROOT / "catalog_import/sources.jsonl").read_text().splitlines() if (s := json.loads(line))}
    reports = ROOT / "catalog_import/reports"
    candidates = ROOT / "catalog_import/candidates"
    reports.mkdir(exist_ok=True)
    candidates.mkdir(exist_ok=True)
    records = {r["source_id"]: r for r in ledger["records"]}
    selected = [pid for pid in BATCH if not args.ids or pid in args.ids]
    work = []
    skipped = []
    for pid in selected:
        spec = BATCH[pid]
        record = records[pid]
        if record["status"] in {"overlap", "excluded"}:
            if args.ids:
                raise ValueError(f"{pid}: cannot import an overlap or excluded interface")
            skipped.append(pid)
            continue
        if not args.force and cached_validation_is_current(pid, spec, record["source_hash"], record):
            skipped.append(pid)
            continue
        work.append((pid, spec, sources[pid], record["source_hash"]))

    results = {}
    started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=min(args.jobs, max(1, len(work)))) as executor:
        futures = {executor.submit(review_isolated, pid, spec, source, source_hash, args.timeout_seconds): pid
                   for pid, spec, source, source_hash in work}
        for future in as_completed(futures):
            pid = futures[future]
            results[pid] = future.result()

    # A single parent is the only writer for candidates, reports, and the ledger.
    for pid, spec, source, source_hash in work:
        payload, report = results[pid]
        record = records[pid]
        problem_id = f"leetcode-{pid}"
        report_path = reports / f"{problem_id}.json"
        write_json_atomic(report_path, report)
        if payload is not None:
            write_json_atomic(candidates / f"{problem_id}.json", payload, compact=True)
        record.update(status="imported" if report["valid"] else "quarantined",
                      problem_id=problem_id, validation_report=str(report_path.relative_to(ROOT)),
                      reason="Reviewed contract and independent oracle; see validation report." if report["valid"] else "Failed validation; excluded from runnable catalog.")
        print(problem_id, "PASS" if report["valid"] else report["failures"], flush=True)
    ledger["counts"] = dict(Counter(r["status"] for r in ledger["records"]))
    if work:
        write_json_atomic(ledger_path, ledger)
    print(json.dumps({"validated": len(work), "reused": len(skipped), "elapsed_seconds": round(time.perf_counter() - started, 3),
                      "counts": ledger["counts"]}), flush=True)


if __name__ == "__main__":
    main()
