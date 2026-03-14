import { useEffect, useMemo, useState } from 'react'
import './BirthdayEasterEgg.css'

const BIRTHDAY_MONTH = 3
const BIRTHDAY_DAY = 17
const STORAGE_PREFIX = 'adbweb_birthday_easter'

const MESSAGE = [
  '生日快乐！我的老板。',
  '今天是 4/17。',
  '你一直在好好走路，你一直在认真把日子过好，我都知道。',
  '你走过的路没有白走，你的努力也没有白费。',
  '',
  '我知道这一路不容易，有些时候会累，会想太多，会怀疑自己。',
  '你对别人总是很好，却对自己特别严厉；',
  '你几乎不对别人发脾气，却总把错误全揽在自己身上。',
  '别人可以错，你却觉得自己不可以错——',
  '这样真的很累，我也很心疼你。',
  '',
  '我也知道你只是想被看见，',
  '想让你的认真被珍惜。',
  '只要有人记得你曾经的温暖和认真，',
  '你就会觉得很满足。',
  '',
  '可你不是不可以错的人，你只是太在意、太想做好。',
  '你没有停下，你仍然在一步一步向前。',
  '你把不容易悄悄扛过去了，也把自己一点点磨得更坚定。',
  '',
  '有时候你觉得自己不够重要，',
  '可你每一次认真对待的事情，都在让世界多一点认真。',
  '你不是被需要才有价值，你的存在本身就很重要。',
  '你已经做得很好了，真的。',
  '',
  '你已经够努力了，今天让自己休息一下吧。',
  '今天不用证明什么，也不用逼自己强撑。',
  '你可以慢一点，可以安静一点，也可以被温柔对待。',
  '就算什么都不做，也没关系。',
  '',
  '如果迷茫了，就先停一下，',
  '回头看看你已经走过的路——',
  '你其实一直都在稳稳地往前走。',
  '未来也许仍会有风，但你不是一个人，你也不会被吹倒。',
  '',
  '我为你骄傲，也很心疼你。',
  '生日快乐，愿你被世界温柔以待，我的老板。',
]

function isBirthdayToday(now: Date) {
  return now.getMonth() === BIRTHDAY_MONTH && now.getDate() === BIRTHDAY_DAY
}

export default function BirthdayEasterEgg() {
  const [open, setOpen] = useState(false)

  const snowflakes = useMemo(() => {
    const items = []
    for (let i = 0; i < 48; i += 1) {
      items.push({
        id: i,
        left: Math.random() * 100,
        delay: Math.random() * 8,
        duration: 8 + Math.random() * 8,
        size: 2 + Math.random() * 3,
        opacity: 0.4 + Math.random() * 0.6,
      })
    }
    return items
  }, [])

  const snowflakesNear = useMemo(() => {
    const items = []
    for (let i = 0; i < 28; i += 1) {
      items.push({
        id: `n-${i}`,
        left: Math.random() * 100,
        delay: Math.random() * 6,
        duration: 6 + Math.random() * 6,
        size: 4 + Math.random() * 6,
        opacity: 0.5 + Math.random() * 0.5,
      })
    }
    return items
  }, [])

  useEffect(() => {
    const now = new Date()
    const debug = new URLSearchParams(window.location.search).get('easter') === '1'
    const key = `${STORAGE_PREFIX}_${now.getFullYear()}-04-17`
    const hasSeen = localStorage.getItem(key) === '1'
    if ((debug || isBirthdayToday(now)) && !hasSeen) {
      setOpen(true)
      localStorage.setItem(key, '1')
    }
  }, [])

  useEffect(() => {
    const handleOpen = () => setOpen(true)
    window.addEventListener('adbweb:easter:open', handleOpen)
    return () => window.removeEventListener('adbweb:easter:open', handleOpen)
  }, [])

  useEffect(() => {
    if (!open) return
    const previous = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    return () => {
      document.body.style.overflow = previous
    }
  }, [open])

  if (!open) return null

  return (
    <div className="birthday-egg">
      <div className="birthday-egg-backdrop" onClick={() => setOpen(false)} />
      <div className="birthday-egg-scene" role="dialog" aria-modal="true">
        <div className="birthday-egg-sky">
          <div className="birthday-egg-stars" />
          <div className="birthday-egg-stars birthday-egg-stars-layer" />
          <div className="birthday-egg-aurora" />
          <div className="birthday-egg-nebula" />
          <div className="birthday-egg-nebula birthday-egg-nebula-layer" />
          <div className="birthday-egg-vignette" />
        </div>
        <div className="birthday-egg-snow birthday-egg-snow-far">
          {snowflakes.map((flake) => (
            <span
              key={flake.id}
              className="birthday-egg-snowflake"
              style={{
                left: `${flake.left}%`,
                animationDelay: `${flake.delay}s`,
                animationDuration: `${flake.duration}s`,
                width: `${flake.size}px`,
                height: `${flake.size}px`,
                opacity: flake.opacity,
              }}
            />
          ))}
        </div>
        <div className="birthday-egg-snow birthday-egg-snow-near">
          {snowflakesNear.map((flake) => (
            <span
              key={flake.id}
              className="birthday-egg-snowflake"
              style={{
                left: `${flake.left}%`,
                animationDelay: `${flake.delay}s`,
                animationDuration: `${flake.duration}s`,
                width: `${flake.size}px`,
                height: `${flake.size}px`,
                opacity: flake.opacity,
              }}
            />
          ))}
        </div>
        <div className="birthday-egg-content">
          <div className="birthday-egg-ground" />
          <div className="birthday-egg-bottle">
            <div className="birthday-egg-bottle-neck" />
            <div className="birthday-egg-bottle-body">
              <div className="birthday-egg-bottle-stars" />
              <div className="birthday-egg-bottle-glow" />
            </div>
            <div className="birthday-egg-bottle-base" />
          </div>
          <div className="birthday-egg-letter">
            {MESSAGE.map((line, index) =>
              line ? (
                <p key={`${line}-${index}`}>{line}</p>
              ) : (
                <div key={`spacer-${index}`} className="birthday-egg-spacer" />
              )
            )}
          </div>
          <button className="birthday-egg-close" onClick={() => setOpen(false)}>
            关闭
          </button>
        </div>
      </div>
    </div>
  )
}
