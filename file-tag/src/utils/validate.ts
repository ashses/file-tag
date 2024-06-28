import type { FormRules, FormItemRule } from 'naive-ui'

// 校验器
const REGEXP_FILE_PATH =
  /^([a-zA-Z]:\\|\/)([a-zA-Z0-9_\-\u4e00-\u9fa5]+(\\|\/)?)*([a-zA-Z0-9_\-\u4e00-\u9fa5]+(\.[a-zA-Z0-9]+)?)?$/

export const validateAddFileRule: FormRules = {
  abs_path: [
    {
      required: false,
      validator(rule: FormItemRule, value: string) {
        if (!REGEXP_FILE_PATH.test(value)) {
          return new Error('请输入正确的文件路径')
        }
        return true
      },
      trigger: ['input', 'blur']
    }
  ]
}
