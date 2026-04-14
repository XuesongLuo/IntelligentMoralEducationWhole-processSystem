<template>
  <div class="question-card" :id="`question-${question.id}`">
    <div class="q-title">
      <span class="title-index">{{ index + 1 }}.</span>
      <template v-if="question.type === 'blank'">
        <span class="inline-fragments">
          <template v-for="(segment, segmentIndex) in titleSegments.parts" :key="`title-${segmentIndex}`">
            <span v-if="segment">{{ segment }}</span>
            <el-input
              v-if="segmentIndex < titleSegments.blankCount"
              :model-value="blankValue[segmentIndex] || ''"
              class="inline-input"
              placeholder="请填写"
              @update:model-value="updateBlankValue(segmentIndex, $event)"
            />
          </template>
        </span>
      </template>
      <template v-else>
        <span>{{ question.title }}</span>
      </template>
      <span class="required">*</span>
    </div>

    <div class="q-body">
      <template v-if="question.type === 'single'">
        <el-radio-group :model-value="singleValue.selected" @update:model-value="updateSingleSelected">
          <el-radio
            v-for="opt in optionMeta"
            :key="opt.value"
            :value="opt.value"
          >
            <span class="option-content">
              <template v-for="(segment, segmentIndex) in opt.parts" :key="`${opt.value}-${segmentIndex}`">
                <span v-if="segment">{{ segment }}</span>
                <el-input
                  v-if="segmentIndex < opt.blankCount"
                  :model-value="getOptionExtraValue('single', opt.value, segmentIndex)"
                  class="inline-input option-inline-input"
                  placeholder="请填写"
                  :disabled="singleValue.selected !== opt.value"
                  @update:model-value="updateOptionExtra('single', opt.value, segmentIndex, $event)"
                  @click.stop
                />
              </template>
            </span>
          </el-radio>
        </el-radio-group>
      </template>

      <template v-else-if="question.type === 'multiple'">
        <el-checkbox-group :model-value="multipleValue.selected" @update:model-value="updateMultipleSelected">
          <el-checkbox
            v-for="opt in optionMeta"
            :key="opt.value"
            :value="opt.value"
          >
            <span class="option-content">
              <template v-for="(segment, segmentIndex) in opt.parts" :key="`${opt.value}-${segmentIndex}`">
                <span v-if="segment">{{ segment }}</span>
                <el-input
                  v-if="segmentIndex < opt.blankCount"
                  :model-value="getOptionExtraValue('multiple', opt.value, segmentIndex)"
                  class="inline-input option-inline-input"
                  placeholder="请填写"
                  :disabled="!multipleValue.selected.includes(opt.value)"
                  @update:model-value="updateOptionExtra('multiple', opt.value, segmentIndex, $event)"
                  @click.stop
                />
              </template>
            </span>
          </el-checkbox>
        </el-checkbox-group>
      </template>

      <template v-else-if="question.type === 'judge'">
        <el-radio-group v-model="localValue">
          <el-radio :value="true">对</el-radio>
          <el-radio :value="false">错</el-radio>
        </el-radio-group>
      </template>

      <template v-else-if="question.type === 'essay'">
        <el-input
          v-model="localValue"
          type="textarea"
          :rows="5"
          maxlength="1000"
          show-word-limit
          placeholder="请输入内容"
        />
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const BLANK_PATTERN = /_{2,}/g

const props = defineProps({
  question: {
    type: Object,
    required: true
  },
  modelValue: {
    type: [String, Number, Boolean, Array, Object],
    default: ''
  },
  index: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['update:modelValue'])

function parseBlankSegments(text) {
  const source = String(text || '')
  const matches = [...source.matchAll(BLANK_PATTERN)]
  if (!matches.length) {
    return {
      parts: [source],
      blankCount: 0
    }
  }

  const parts = []
  let lastIndex = 0
  matches.forEach(match => {
    parts.push(source.slice(lastIndex, match.index))
    lastIndex = match.index + match[0].length
  })
  parts.push(source.slice(lastIndex))

  return {
    parts,
    blankCount: matches.length
  }
}

function buildEmptyExtraMap() {
  return {}
}

function normalizeBlankModel(value, blankCount) {
  if (Array.isArray(value)) {
    const next = value.slice(0, blankCount)
    while (next.length < blankCount) next.push('')
    return next
  }
  if (blankCount <= 1) {
    return [value ?? '']
  }
  return Array.from({ length: blankCount }, (_, index) => {
    if (Array.isArray(value)) return value[index] ?? ''
    return ''
  })
}

function normalizeSingleModel(value) {
  if (value && typeof value === 'object' && !Array.isArray(value)) {
    return {
      selected: value.selected ?? '',
      extras: value.extras && typeof value.extras === 'object' ? { ...value.extras } : buildEmptyExtraMap()
    }
  }
  return {
    selected: value ?? '',
    extras: buildEmptyExtraMap()
  }
}

function normalizeMultipleModel(value) {
  if (value && typeof value === 'object' && !Array.isArray(value)) {
    return {
      selected: Array.isArray(value.selected) ? [...value.selected] : [],
      extras: value.extras && typeof value.extras === 'object' ? { ...value.extras } : buildEmptyExtraMap()
    }
  }
  return {
    selected: Array.isArray(value) ? [...value] : [],
    extras: buildEmptyExtraMap()
  }
}

const titleSegments = computed(() => parseBlankSegments(props.question.title))

const optionMeta = computed(() =>
  (props.question.options || []).map(opt => {
    const parsed = parseBlankSegments(opt.label)
    return {
      ...opt,
      parts: parsed.parts,
      blankCount: parsed.blankCount
    }
  })
)

const blankValue = computed(() => normalizeBlankModel(props.modelValue, Math.max(titleSegments.value.blankCount, 1)))
const singleValue = computed(() => normalizeSingleModel(props.modelValue))
const multipleValue = computed(() => normalizeMultipleModel(props.modelValue))

const localValue = computed({
  get() {
    return props.modelValue
  },
  set(val) {
    emit('update:modelValue', val)
  }
})

function updateBlankValue(index, value) {
  const next = [...blankValue.value]
  next[index] = value
  emit('update:modelValue', next)
}

function updateSingleSelected(value) {
  emit('update:modelValue', {
    selected: value,
    extras: { ...singleValue.value.extras }
  })
}

function updateMultipleSelected(values) {
  emit('update:modelValue', {
    selected: Array.isArray(values) ? values : [],
    extras: { ...multipleValue.value.extras }
  })
}

function getOptionExtraValue(questionType, optionValue, index) {
  const extras = questionType === 'single' ? singleValue.value.extras : multipleValue.value.extras
  const optionExtras = extras?.[optionValue]
  if (Array.isArray(optionExtras)) {
    return optionExtras[index] || ''
  }
  if (index === 0 && typeof optionExtras === 'string') {
    return optionExtras
  }
  return ''
}

function updateOptionExtra(questionType, optionValue, index, value) {
  const current = questionType === 'single' ? singleValue.value : multipleValue.value
  const nextExtras = { ...current.extras }
  const optionMetaItem = optionMeta.value.find(item => item.value === optionValue)
  const blankCount = optionMetaItem?.blankCount || 1
  const optionExtras = Array.isArray(nextExtras[optionValue])
    ? [...nextExtras[optionValue]]
    : Array.from({ length: blankCount }, (_, itemIndex) => {
        if (itemIndex === 0 && typeof nextExtras[optionValue] === 'string') {
          return nextExtras[optionValue]
        }
        return ''
      })
  optionExtras[index] = value
  nextExtras[optionValue] = optionExtras

  if (questionType === 'single') {
    emit('update:modelValue', {
      selected: current.selected,
      extras: nextExtras
    })
    return
  }

  emit('update:modelValue', {
    selected: [...current.selected],
    extras: nextExtras
  })
}
</script>

<style scoped>
.question-card {
  border: 1px solid #dcdfe6;
  padding: 20px;
  margin-bottom: 18px;
  border-radius: 8px;
  transition: box-shadow 0.25s ease, border-color 0.25s ease, background-color 0.25s ease;
}

.question-card.question-focus {
  border-color: #e6a23c;
  box-shadow: 0 0 0 3px rgba(230, 162, 60, 0.18);
  background: #fffaf0;
}

.q-title {
  margin-bottom: 16px;
  font-size: 18px;
  line-height: 1.8;
  font-weight: 600;
}

.title-index {
  margin-right: 6px;
}

.inline-fragments,
.option-content {
  display: inline-flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  line-height: 1.8;
}

.inline-input {
  width: 140px;
  vertical-align: middle;
}

.option-inline-input {
  margin: 0 6px;
}

.required {
  color: #f56c6c;
  margin-left: 4px;
}

.q-body {
  padding-left: 12px;
}

:deep(.el-radio),
:deep(.el-checkbox) {
  display: block;
  margin-bottom: 14px;
  height: auto;
}

:deep(.el-radio__label),
:deep(.el-checkbox__label) {
  white-space: normal;
}
</style>
