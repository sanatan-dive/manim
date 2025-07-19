

function Header() {
  return (
    <div className=' fixed inset-0'>
        <div className='flex justify-between items-center'>
      <div className='font-funnel flex items-center gap-1 m-4 cursor-pointer '>
        <div className='w-4 h-4 bg-black border rounded-full translate-y-0.5 '></div>
        <h1 className='text-xl font-medium'>Madio</h1>
      </div>

      <div className='font-funnel flex items-center gap-4 m-4'>
        <span className='text-sm hover:text-stone-500 duration-200 cursor-pointer'>Motive</span>
        <span className='text-sm hover:text-stone-500 duration-200 cursor-pointer'>Works</span>
        <span className='text-sm hover:text-stone-500 duration-200 cursor-pointer'>Dashboard</span>
      </div>
      <div>
        <button className='bg-black text-white font-funnel m-4 px-4 py-2 text-sm rounded-full hover:bg-black/80 duration-200 cursor-pointer  '>Sign In</button>
      </div>
      </div>
    </div>
  )
}

export default Header