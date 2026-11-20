// Small dialogs and helpers shared by the screens.

import { alertController, toastController } from '@ionic/vue'

export async function say(header: string, message: string): Promise<void> {
  const a = await alertController.create({ header, message, buttons: ['Добре'] })
  await a.present()
  await a.onDidDismiss()
}

export async function ask(header: string, message: string, okText = 'Так', danger = false): Promise<boolean> {
  const a = await alertController.create({
    header,
    message,
    buttons: [
      { text: 'Скасувати', role: 'cancel' },
      { text: okText, role: 'confirm', cssClass: danger ? 'nmt-danger' : undefined },
    ],
  })
  await a.present()
  return (await a.onDidDismiss()).role === 'confirm'
}

export async function toast(message: string, color = 'dark'): Promise<void> {
  const t = await toastController.create({ message, duration: 2500, color, position: 'top' })
  await t.present()
}

/** Saves text as a file in the browser (reports). */
export function downloadText(filename: string, text: string): void {
  const url = URL.createObjectURL(new Blob([text], { type: 'text/plain;charset=utf-8' }))
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}

export function reportFileName(d: Date = new Date()): string {
  const p = (n: number) => String(n).padStart(2, '0')
  return `nmt_report_${d.getFullYear()}${p(d.getMonth() + 1)}${p(d.getDate())}_${p(d.getHours())}${p(d.getMinutes())}.txt`
}
