<template>
    <div class="auth-field">
        <label v-if="label" class="auth-field__label">{{ label }}</label>

        <div class="auth-field__wrapper" :class="statusClass">
        <div class="auth-field__icon">{{ icon }}</div>

        <input
            :type="type"
            :value="modelValue"
            :placeholder="placeholder"
            class="auth-field__input"
            @input="$emit('update:modelValue', $event.target.value)"
        />

        <button
            v-if="actionText"
            type="button"
            class="auth-field__action"
            @click="$emit('action')"
        >
            {{ actionText }}
        </button>

        <div v-if="status === 'success'" class="auth-field__status success">✔</div>
        <div v-else-if="status === 'error'" class="auth-field__status error">✖</div>
        <div v-else-if="status === 'help'" class="auth-field__status help">?</div>
        </div>

        <div v-if="errorMessage" class="auth-field__error">{{ errorMessage }}</div>
        <div v-if="hint" class="auth-field__hint">{{ hint }}</div>
    </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
    modelValue: {
        type: String,
        default: ''
    },
    label: {
        type: String,
        default: ''
    },
    placeholder: {
        type: String,
        default: ''
    },
    type: {
        type: String,
        default: 'text'
    },
    icon: {
        type: String,
        default: '○'
    },
    status: {
        type: String,
        default: ''
    },
    errorMessage: {
        type: String,
        default: ''
    },
    hint: {
        type: String,
        default: ''
    },
    actionText: {
        type: String,
        default: ''
    }
})

const statusClass = computed(() => {
    if (props.status === 'success') return 'is-success'
    if (props.status === 'error') return 'is-error'
    return ''
})
</script>


<style scoped>
.auth-field {
  margin-bottom: 28px;
}

.auth-field__label {
  display: block;
  margin-bottom: 8px;
  color: #333;
  font-size: 14px;
}

.auth-field__wrapper {
  display: flex;
  align-items: center;
  height: 58px;
  border: 1px solid #cfcfcf;
  background: #fff;
}

.auth-field__icon {
  width: 52px;
  text-align: center;
  font-size: 22px;
  color: #222;
  flex-shrink: 0;
}

.auth-field__input {
  flex: 1;
  height: 100%;
  border: none;
  outline: none;
  font-size: 18px;
  color: #222;
}

.auth-field__input::placeholder {
  color: #666;
}

.auth-field__status {
  width: 48px;
  text-align: center;
  font-size: 24px;
  flex-shrink: 0;
}

.auth-field__status.success {
  color: #8bc34a;
}

.auth-field__status.error {
  color: #e74c3c;
}

.auth-field__status.help {
  color: #333;
}

.auth-field__action {
  border: none;
  background: transparent;
  color: #5daaf7;
  font-size: 16px;
  padding: 0 14px;
  cursor: pointer;
  white-space: nowrap;
}

.auth-field__error {
  color: #e74c3c;
  font-size: 13px;
  margin-top: 6px;
}

.auth-field__hint {
  color: #999;
  font-size: 13px;
  margin-top: 6px;
}
</style>