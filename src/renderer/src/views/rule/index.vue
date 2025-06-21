<template>
  <div class="rule-container">
    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <el-input
        v-model="searchQuery"
        placeholder="搜索规则"
        class="search-input"
        clearable
        @input="handleSearch"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>

      <div class="sort-options">
        <el-radio-group v-model="sortBy" size="small" @change="handleSortChange">
          <el-radio-button label="updated_at">时间排序</el-radio-button>
          <el-radio-button label="name">名称排序</el-radio-button>
        </el-radio-group>
      </div>

      <el-button type="primary" @click="openRuleDialog">
        <el-icon><Plus /></el-icon>
        新建规则
      </el-button>
    </div>

    <!-- 规则列表 -->
    <div class="rule-content">
      <el-empty v-if="filteredRules.length === 0" description="暂无规则" />

      <div v-else class="rule-grid">
        <div v-for="rule in filteredRules" :key="rule.id" class="rule-card">
          <div class="rule-header">
            <h3 class="rule-name">{{ rule.name }}</h3>
            <div class="rule-actions">
              <el-button size="small" @click="openRuleDialog(rule)">
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button size="small" type="danger" @click="confirmDeleteRule(rule)">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </div>
          </div>
          <div class="rule-info">
            <p>
              <span class="label">来源网址：</span>
              <el-link :href="rule.source_url" target="_blank" type="primary" :underline="false">
                {{ rule.source_url }}
              </el-link>
            </p>
            <p>
              <span class="label">查询网址：</span>
              <el-tooltip :content="rule.search_url" placement="top">
                <span class="ellipsis">{{ rule.search_url }}</span>
              </el-tooltip>
            </p>
            <p>
              <span class="label">搜索结果规则：</span>
              <el-tooltip :content="rule.search_result_rule || '无'" placement="top">
                <span class="ellipsis">{{ rule.search_result_rule || '无' }}</span>
              </el-tooltip>
            </p>
            <p>
              <span class="label">封面规则：</span>
              <el-tooltip :content="rule.cover_rule || '无'" placement="top">
                <span class="ellipsis">{{ rule.cover_rule || '无' }}</span>
              </el-tooltip>
            </p>
            <p>
              <span class="label">书名规则：</span>
              <el-tooltip :content="rule.title_rule" placement="top">
                <span class="ellipsis">{{ rule.title_rule }}</span>
              </el-tooltip>
            </p>
            <p>
              <span class="label">作者规则：</span>
              <el-tooltip :content="rule.author_rule || '无'" placement="top">
                <span class="ellipsis">{{ rule.author_rule || '无' }}</span>
              </el-tooltip>
            </p>
            <p>
              <span class="label">详情规则：</span>
              <el-tooltip :content="rule.description_rule || '无'" placement="top">
                <span class="ellipsis">{{ rule.description_rule || '无' }}</span>
              </el-tooltip>
            </p>
            <p>
              <span class="label">章节规则：</span>
              <el-tooltip :content="rule.chapter_list_rule" placement="top">
                <span class="ellipsis">{{ rule.chapter_list_rule }}</span>
              </el-tooltip>
            </p>
            <p>
              <span class="label">内容规则：</span>
              <el-tooltip :content="rule.chapter_content_rule" placement="top">
                <span class="ellipsis">{{ rule.chapter_content_rule }}</span>
              </el-tooltip>
            </p>
          </div>
        </div>
      </div>

      <el-pagination
        v-if="total > pageSize"
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 30, 40]"
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 规则表单对话框 -->
    <el-dialog
      v-model="ruleDialogVisible"
      :title="isEdit ? '编辑规则' : '新建规则'"
      width="50%"
      :close-on-click-modal="false"
    >
      <el-form
        ref="ruleFormRef"
        :model="ruleForm"
        :rules="ruleRules"
        label-width="100px"
        label-position="right"
      >
        <el-form-item label="规则名称" prop="name">
          <el-input v-model="ruleForm.name" placeholder="请输入规则名称" />
        </el-form-item>
        <el-form-item label="来源网址" prop="source_url">
          <el-input v-model="ruleForm.source_url" placeholder="请输入来源网址" />
        </el-form-item>
        <el-form-item label="查询网址" prop="search_url">
          <el-input v-model="ruleForm.search_url" placeholder="请输入查询网址，使用{keyword}作为搜索关键词占位符" />
        </el-form-item>
        <el-form-item label="搜索结果规则" prop="search_result_rule">
          <el-input v-model="ruleForm.search_result_rule" placeholder="请输入搜索结果提取规则（可选）" />
        </el-form-item>
        <el-form-item label="封面规则" prop="cover_rule">
          <el-input v-model="ruleForm.cover_rule" placeholder="请输入封面规则（可选）" />
        </el-form-item>
        <el-form-item label="书名规则" prop="title_rule">
          <el-input v-model="ruleForm.title_rule" placeholder="请输入书名规则" />
        </el-form-item>
        <el-form-item label="作者规则" prop="author_rule">
          <el-input v-model="ruleForm.author_rule" placeholder="请输入作者规则（可选）" />
        </el-form-item>
        <el-form-item label="详情规则" prop="description_rule">
          <el-input v-model="ruleForm.description_rule" placeholder="请输入详情规则（可选）" />
        </el-form-item>
        <el-form-item label="章节规则" prop="chapter_list_rule">
          <el-input v-model="ruleForm.chapter_list_rule" placeholder="请输入章节列表规则" />
        </el-form-item>
        <el-form-item label="内容规则" prop="chapter_content_rule">
          <el-input v-model="ruleForm.chapter_content_rule" placeholder="请输入章节内容规则" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="ruleDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitRuleForm">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 删除确认对话框 -->
    <el-dialog
      v-model="deleteDialogVisible"
      title="删除确认"
      width="30%"
      :close-on-click-modal="false"
    >
      <span>确定要删除规则「{{ ruleToDelete?.name }}」吗？</span>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="deleteDialogVisible = false">取消</el-button>
          <el-button type="danger" @click="deleteRule">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Plus, Edit, Delete } from '@element-plus/icons-vue'
import { getRules, getRule, createRule, updateRule, deleteRule as apiDeleteRule } from '@/api/rule'
import type { FormInstance, FormRules } from 'element-plus'

// 分页相关
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 排序和搜索
const sortBy = ref('updated_at')
const searchQuery = ref('')

// 规则数据
const rules = ref([])
const loading = ref(false)

// 规则表单相关
const ruleFormRef = ref<FormInstance>()
const ruleDialogVisible = ref(false)
const isEdit = ref(false)
const ruleForm = reactive({
  id: 0,
  name: '',
  source_url: '',
  search_url: '',
  search_result_rule: '',
  cover_rule: '',
  title_rule: '',
  author_rule: '',
  description_rule: '',
  chapter_list_rule: '',
  chapter_content_rule: ''
})

// 表单验证规则
const ruleRules = reactive<FormRules>({
  name: [
    { required: true, message: '请输入规则名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  source_url: [
    { required: true, message: '请输入来源网址', trigger: 'blur' },
    { type: 'url', message: '请输入有效的URL', trigger: 'blur' }
  ],
  search_url: [
    { required: true, message: '请输入查询网址', trigger: 'blur' },
    { validator: (rule, value, callback) => {
      if (value && !value.includes('{keyword}')) {
        callback(new Error('查询网址必须包含{keyword}作为搜索关键词占位符'))
      } else {
        callback()
      }
    }, trigger: 'blur' }
  ],
  title_rule: [
    { required: true, message: '请输入书名规则', trigger: 'blur' }
  ],
  chapter_list_rule: [
    { required: true, message: '请输入章节列表规则', trigger: 'blur' }
  ],
  chapter_content_rule: [
    { required: true, message: '请输入章节内容规则', trigger: 'blur' }
  ]
})

// 删除相关
const deleteDialogVisible = ref(false)
const ruleToDelete = ref(null)

// 过滤后的规则列表
const filteredRules = computed(() => {
  // 确保rules.value是数组
  if (!Array.isArray(rules.value)) {
    console.warn('rules.value不是数组:', rules.value)
    return []
  }
  
  if (!searchQuery.value) {
    return rules.value
  }
  
  const query = searchQuery.value.toLowerCase()
  return rules.value.filter(rule => {
    // 添加空值检查
    if (!rule) return false
    
    return (rule.name && rule.name.toLowerCase().includes(query)) || 
           (rule.source_url && rule.source_url.toLowerCase().includes(query))
  })
})

// 获取规则数据
const fetchRules = async () => {
  loading.value = true
  try {
    const response = await getRules(currentPage.value, pageSize.value, sortBy.value)
    console.log('获取规则列表返回数据:', response) // 调试输出
    
    // 检查返回的数据结构
    if (response) {
      // 根据后端API的实际返回结构处理数据
      if (response.data) {
        // 情况1: 标准结构 {data: {...}}
        if (Array.isArray(response.data.items)) {
          // 情况1.1: {data: {items: [...], total: number}}
          rules.value = response.data.items
          total.value = response.data.total || 0
        } else if (Array.isArray(response.data)) {
          // 情况1.2: {data: [...]}
          rules.value = response.data
          total.value = response.total || response.data.length || 0
        } else {
          // 情况1.3: 其他结构
          console.error('API返回的data字段结构不符合预期:', response.data)
          rules.value = []
          total.value = 0
        }
      } else if (Array.isArray(response)) {
        // 情况2: response本身是数组
        rules.value = response
        total.value = response.length
      } else if (response.items && Array.isArray(response.items)) {
        // 情况3: {items: [...], total: number}
        rules.value = response.items
        total.value = response.total || response.items.length || 0
      } else {
        // 情况4: 未知结构
        console.error('API返回的数据结构不符合预期:', response)
        rules.value = []
        total.value = 0
        ElMessage.warning('数据格式异常，请联系管理员')
      }
    } else {
      console.error('API返回的数据为空')
      rules.value = []
      total.value = 0
    }
    
    // 确保rules.value是数组
    if (!Array.isArray(rules.value)) {
      console.error('处理后的rules不是数组:', rules.value)
      rules.value = []
    }
  } catch (error) {
    console.error('获取规则数据失败:', error)
    ElMessage.error('获取规则数据失败，请稍后重试')
    rules.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

// 处理搜索
const handleSearch = () => {
  // 本地搜索，不需要重新请求
}

// 处理排序变化
const handleSortChange = () => {
  currentPage.value = 1
  fetchRules()
}

// 处理分页大小变化
const handleSizeChange = (size: number) => {
  pageSize.value = size
  fetchRules()
}

// 处理分页页码变化
const handleCurrentChange = (page: number) => {
  currentPage.value = page
  fetchRules()
}

// 打开规则对话框
const openRuleDialog = async (rule = null) => {
  // 重置表单和状态
  resetRuleForm()
  isEdit.value = false
  
  // 先显示对话框，避免用户等待
  ruleDialogVisible.value = true
  
  // 如果传入了规则对象且有ID，则是编辑模式
  if (rule && rule.id) {
    isEdit.value = true
    try {
      const response = await getRule(rule.id)
      console.log('获取规则详情返回:', response) // 调试输出
      
      // 检查返回的数据结构
      console.log('规则详情原始数据:', response)
      
      // 处理不同的数据结构情况
      let ruleData = null
      
      if (response && response.data) {
        // 情况1: response 包含 data 字段
        ruleData = response.data
      } else if (response && typeof response === 'object' && 'id' in response) {
        // 情况2: response 本身就是规则数据
        ruleData = response
      }
      
      if (ruleData) {
        console.log('处理后的规则数据:', ruleData)
        // 将API返回的数据填充到表单中
        Object.keys(ruleForm).forEach(key => {
          if (key in ruleData) {
            ruleForm[key] = ruleData[key]
          }
        })
      } else {
        console.error('获取规则详情返回的数据结构不符合预期')
        ElMessage.warning('获取规则详情失败，数据格式异常')
      }
    } catch (error) {
      console.error('获取规则详情失败:', error)
      ElMessage.error('获取规则详情失败，请稍后重试')
      // 不返回，继续显示对话框让用户可以手动填写
    }
  }
  // 新建规则的情况不需要额外处理，因为已经重置了表单
}

// 重置规则表单
const resetRuleForm = () => {
  if (ruleFormRef.value) {
    ruleFormRef.value.resetFields()
  }
  
  ruleForm.id = 0
  ruleForm.name = ''
  ruleForm.source_url = ''
  ruleForm.search_url = ''
  ruleForm.search_result_rule = ''
  ruleForm.cover_rule = ''
  ruleForm.title_rule = ''
  ruleForm.author_rule = ''
  ruleForm.description_rule = ''
  ruleForm.chapter_list_rule = ''
  ruleForm.chapter_content_rule = ''
}

// 提交规则表单
const submitRuleForm = async () => {
  if (!ruleFormRef.value) {
    console.warn('表单引用不存在')
    return
  }
  
  await ruleFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        // 准备提交的数据
        const ruleData = {
          name: ruleForm.name,
          source_url: ruleForm.source_url,
          search_url: ruleForm.search_url,
          search_result_rule: ruleForm.search_result_rule || '',
          cover_rule: ruleForm.cover_rule || '',
          title_rule: ruleForm.title_rule,
          author_rule: ruleForm.author_rule || '',
          description_rule: ruleForm.description_rule || '',
          chapter_list_rule: ruleForm.chapter_list_rule,
          chapter_content_rule: ruleForm.chapter_content_rule
        }
        
        console.log(`准备${isEdit.value ? '更新' : '创建'}规则:`, ruleData)
        
        let response
        try {
          if (isEdit.value) {
            response = await updateRule(ruleForm.id, ruleData)
            console.log('更新规则响应:', response)
            ElMessage.success('规则更新成功')
          } else {
            response = await createRule(ruleData)
            console.log('创建规则响应:', response)
            ElMessage.success('规则创建成功')
          }
          
          // 关闭对话框
          ruleDialogVisible.value = false
          
          // 延迟一下再刷新列表，确保后端数据已更新
          setTimeout(async () => {
            try {
              await fetchRules() // 刷新规则列表
            } catch (refreshError) {
              console.error('刷新规则列表失败:', refreshError)
            }
          }, 300)
        } catch (apiError) {
          throw apiError // 将API错误传递给外层catch
        }
      } catch (error) {
        console.error('保存规则失败:', error)
        if (error.response) {
          console.error('错误响应:', error.response.data)
          let errorMsg = '请稍后重试'
          if (error.response.data) {
            if (typeof error.response.data === 'string') {
              errorMsg = error.response.data
            } else if (error.response.data.message) {
              errorMsg = error.response.data.message
            } else if (error.response.data.detail) {
              errorMsg = error.response.data.detail
            } else if (error.response.data.error) {
              errorMsg = error.response.data.error
            }
          }
          ElMessage.error(`保存规则失败: ${errorMsg}`)
        } else if (error.request) {
          console.error('未收到响应:', error.request)
          ElMessage.error('网络错误，未收到服务器响应')
        } else {
          console.error('请求配置错误:', error.message)
          ElMessage.error(`请求错误: ${error.message}`)
        }
      }
    } else {
      return false
    }
  })
}

// 确认删除规则
const confirmDeleteRule = (rule) => {
  ruleToDelete.value = rule
  deleteDialogVisible.value = true
}

// 删除规则
const deleteRule = async () => {
  if (!ruleToDelete.value) return
  
  try {
    await apiDeleteRule(ruleToDelete.value.id)
    ElMessage.success(`已删除规则「${ruleToDelete.value.name}」`)
    deleteDialogVisible.value = false
    fetchRules()
  } catch (error) {
    console.error('删除规则失败:', error)
    ElMessage.error('删除规则失败，请稍后重试')
  }
}

// 监听搜索查询变化
watch(searchQuery, (newVal) => {
  if (!newVal) {
    // 如果搜索框被清空，重新获取所有数据
    fetchRules()
  }
})

onMounted(() => {
  fetchRules()
})
</script>

<style scoped lang="scss">
.rule-container {
  padding: 20px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;

  .search-input {
    width: 300px;
  }

  .sort-options {
    display: flex;
    align-items: center;
  }
}

.rule-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.rule-card {
  border-radius: 8px;
  background-color: var(--el-bg-color);
  box-shadow: var(--el-box-shadow-light);
  padding: 16px;
  transition: box-shadow 0.3s;

  &:hover {
    box-shadow: var(--el-box-shadow);
  }

  .rule-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    border-bottom: 1px solid var(--el-border-color-light);
    padding-bottom: 10px;

    .rule-name {
      margin: 0;
      font-size: 18px;
      font-weight: 600;
    }

    .rule-actions {
      display: flex;
      gap: 8px;
    }
  }

  .rule-info {
    p {
      margin: 8px 0;
      display: flex;
      align-items: flex-start;

      .label {
        font-weight: 500;
        min-width: 80px;
        color: var(--el-text-color-secondary);
      }

      .ellipsis {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        flex: 1;
      }
    }
  }
}

.el-pagination {
  margin-top: 20px;
  justify-content: center;
}
</style>