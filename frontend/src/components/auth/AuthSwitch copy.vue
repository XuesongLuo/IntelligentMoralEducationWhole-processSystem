<template>
    <button
        type="button"
        class="role-switch"
        :class="{ 'is-teacher': modelValue === 'teacher' }"
        @click="toggle"
    >
        <span class="role-switch__dot"></span>
    </button>
</template>

<script setup>
const props = defineProps({
    modelValue: {
        type: String,
        default: 'student'
    }
})

const emit = defineEmits(['update:modelValue'])

function toggle() {
    emit('update:modelValue', props.modelValue === 'student' ? 'teacher' : 'student')
}
</script>


<style scoped>
.role-switch {
    width: 76px;
    height: 40px;
    border: none;
    border-radius: 20px;
    background: #18d860;
    position: relative;
    cursor: pointer;
}

.role-switch__dot {
    position: absolute;
    top: 4px;
    left: 38px;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: #fff;
    transition: all 0.2s;
}

.role-switch.is-teacher .role-switch__dot {
    left: 6px;
}
</style>